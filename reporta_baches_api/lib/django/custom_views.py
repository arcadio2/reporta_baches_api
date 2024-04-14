from rest_framework import viewsets, mixins

class CreateListRetrieveViewSet(mixins.CreateModelMixin,
                                mixins.ListModelMixin,
                                mixins.RetrieveModelMixin,
                                viewsets.GenericViewSet):
    pass


class CreateListUpdateRetrieveViewSet(mixins.CreateModelMixin,
                                      mixins.ListModelMixin,
                                      mixins.UpdateModelMixin,
                                      mixins.RetrieveModelMixin,
                                      viewsets.GenericViewSet):
    pass


class ListUpdateRetrieveViewSet(mixins.ListModelMixin,
                                mixins.UpdateModelMixin,
                                mixins.RetrieveModelMixin,
                                viewsets.GenericViewSet):
    pass


class ListViewSet(mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    pass


class ListRetrieveViewset(mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):
    pass


class RetrieveViewSet(mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):
    pass

class CreateListRetrieveDestroyViewSet(mixins.CreateModelMixin,
                                        mixins.UpdateModelMixin,
                                        mixins.ListModelMixin,
                                        mixins.RetrieveModelMixin,
                                        mixins.DestroyModelMixin,
                                        viewsets.GenericViewSet):
    pass

class CreateLisViewSet(mixins.CreateModelMixin,
                               mixins.ListModelMixin,
                               viewsets.GenericViewSet):
    pass