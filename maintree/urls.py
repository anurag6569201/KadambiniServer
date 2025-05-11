from django.urls import path, include
from rest_framework_nested import routers 
from rest_framework.authtoken.views import obtain_auth_token
from .views import (
    FamilyTreeViewSet, PersonViewSet, RelationshipViewSet,
    MedicalConditionViewSet, TimelineEventViewSet, GeneticMarkerViewSet, DocumentViewSet,
    UserRegistrationView, medlineplus_proxy_view
)

# Main router for top-level resources
router = routers.DefaultRouter()
router.register(r'familytrees', FamilyTreeViewSet, basename='familytree')

# Nested router for Persons under a FamilyTree
# URL: /api/familytrees/{tree_pk}/persons/
persons_router = routers.NestedSimpleRouter(router, r'familytrees', lookup='tree')
persons_router.register(r'persons', PersonViewSet, basename='tree-persons')

# Nested router for Relationships under a FamilyTree
# URL: /api/familytrees/{tree_pk}/relationships/
relationships_router = routers.NestedSimpleRouter(router, r'familytrees', lookup='tree')
relationships_router.register(r'relationships', RelationshipViewSet, basename='tree-relationships')

# Nested router for MedicalConditions, TimelineEvents, GeneticMarkers, and Documents under a Person
medicalconditions_router = routers.NestedSimpleRouter(persons_router, r'persons', lookup='person')
medicalconditions_router.register(r'medicalconditions', MedicalConditionViewSet, basename='person-medicalconditions')

timelineevents_router = routers.NestedSimpleRouter(persons_router, r'persons', lookup='person')
timelineevents_router.register(r'timelineevents', TimelineEventViewSet, basename='person-timelineevents')

geneticmarkers_router = routers.NestedSimpleRouter(persons_router, r'persons', lookup='person')
geneticmarkers_router.register(r'geneticmarkers', GeneticMarkerViewSet, basename='person-geneticmarkers')

documents_router = routers.NestedSimpleRouter(persons_router, r'persons', lookup='person')
documents_router.register(r'documents', DocumentViewSet, basename='person-documents')


urlpatterns = [
    path('', include(router.urls)),
    path('', include(persons_router.urls)),
    path('', include(relationships_router.urls)),
    path('', include(medicalconditions_router.urls)),
    path('', include(timelineevents_router.urls)),
    path('', include(geneticmarkers_router.urls)),
    path('', include(documents_router.urls)),

    path('medlineplus-search/', medlineplus_proxy_view, name='medlineplus-search-proxy'),
]
