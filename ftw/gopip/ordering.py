from Acquisition import aq_base
from functools import partial
from plone import api
from plone.folder.default import DefaultOrdering
from plone.folder.interfaces import IExplicitOrdering
from plone.folder.partial import PartialOrdering
from plone.folder.unordered import UnorderedOrdering
from Products.PluginIndexes.FieldIndex.FieldIndex import FieldIndex
import logging


LOG = logging.getLogger('ftw.gopip')

ORDERING_TRACK_METHODS = (
    'notifyAdded',
    'notifyRemoved',
)

EXPLICIT_ORDERING_TRACK_METHODS = (
    'notifyAdded',
    'notifyRemoved',
    'moveObjectsByDelta',
    'moveObjectsUp',
    'moveObjectsDown',
    'moveObjectsToTop',
    'moveObjectsToBottom',
    'moveObjectToPosition',
    'orderObjects',
)


class KeepIndexInSync(object):

    def order_may_have_changed(self, source=None):
        if not self.is_index_replaced():
            # back off
            return
        self.ensure_children_position_updated_in_index()

    def is_index_replaced(self):
        """If the index is not replaced with a FieldIndex, this package
        was not installed in the portal_setup / quick installer and we should
        back off.
        """
        catalog = api.portal.get_tool('portal_catalog')
        try:
            index = catalog._catalog.getIndex('getObjPositionInParent')
        except KeyError:
            return False
        else:
            return isinstance(index, FieldIndex)

    def ensure_children_position_updated_in_index(self):
        catalog = api.portal.get_tool('portal_catalog')

        # Fix an issue when using ftw.gopip in combination with versions from
        # Products.CMFEditions.
        #
        # In some cases we get an ImplicitAcquisitionWrapper-object as
        # the context which will cause errors when accessing
        # object-methods. To fix the issue, we have to get the real
        # content object.
        #
        # Warning: this case is not testet!
        context = aq_base(self.context)

        index = catalog._catalog.getIndex('getObjPositionInParent')
        path = '/'.join(context.getPhysicalPath())
        child_ids_to_index = []

        for position, child_id in enumerate(self.idsInOrder()):
            child_rid = catalog.getrid(path + '/' + child_id)
            if child_rid is None:
                # The child is not yet in the catalog.
                # This means it will probably be indexed later with the correct
                # position and thus we do not need to do anything here.
                continue

            index_position = index.getEntryForObject(child_rid)
            if index_position != position:
                child_ids_to_index.append(child_id)

        for child_id in child_ids_to_index:
            child_object = context[child_id]
            catalog.reindexObject(child_object,
                                  idxs=['getObjPositionInParent'],
                                  update_metadata=False)

    @staticmethod
    def track_methods(klass):
        if IExplicitOrdering.implementedBy(klass):
            methodnames = EXPLICIT_ORDERING_TRACK_METHODS
        else:
            methodnames = ORDERING_TRACK_METHODS

        map(partial(KeepIndexInSync.wrap_method, klass), methodnames)
        return klass

    @staticmethod
    def wrap_method(klass, methodname):
        method = getattr(klass, methodname)
        def wrapper(self, *args, **kwargs):
            result = method(self, *args, **kwargs)
            self.order_may_have_changed(methodname)
            return result
        setattr(klass, methodname, wrapper)


@KeepIndexInSync.track_methods
class DefaultOrderingProxy(DefaultOrdering, KeepIndexInSync):
    pass


@KeepIndexInSync.track_methods
class PartialOrderingProxy(PartialOrdering, KeepIndexInSync):
    pass


@KeepIndexInSync.track_methods
class UnorderedOrderingProxy(UnorderedOrdering, KeepIndexInSync):
    pass
