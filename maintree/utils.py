# familytree/utils.py
import uuid
from datetime import date, timedelta
# Ensure your CustomUser model can be imported if needed for type hinting,
# or just rely on duck-typing (user object having username, first_name, etc.)
# from authentication.models import CustomUser # Optional for type hinting

def get_default_family_tree_data(user=None): # Add user parameter
    """
    Generates a small default family tree structure.
    If a user object is provided, it attempts to use user's details for "Your Name" node.
    Returns a dictionary with 'nodes_data' and 'edges_data'.
    """
    today = date.today()
    
    def format_date(d):
        return d.strftime("%Y-%m-%d")

    grandpa_id = str(uuid.uuid4())
    grandma_id = str(uuid.uuid4())
    father_id = str(uuid.uuid4())
    mother_id = str(uuid.uuid4())
    child1_id = str(uuid.uuid4()) # This will be "You"
    child2_id = str(uuid.uuid4())

    # Default values for the "You" node
    your_name_node_firstname = "Your Name"
    your_name_node_lastname = "User" # Default last name if user has none
    your_name_node_profile_picture = "https://media.istockphoto.com/id/1327592449/vector/default-avatar-photo-placeholder-icon-grey-profile-picture-business-man.jpg?s=612x612&w=0&k=20&c=yqoos7g9jmufJhfkbQsk-mdhKEsih6Di4WZ66t_ib7I=" # Default last name if user has none
    your_name_node_bio = "This is you! Start building your family tree."

    if user:
        if hasattr(user, 'first_name') and user.first_name:
            your_name_node_firstname = user.first_name
        if hasattr(user, 'profile_picture') and user.profile_picture:
            your_name_node_profile_picture = user.profile_picture.url
        if hasattr(user, 'last_name') and user.last_name:
            your_name_node_lastname = user.last_name
        your_name_node_bio = f"This is {your_name_node_firstname}. Start building your family tree."


    default_nodes_data = [
        {
            "id": grandpa_id,
            "type": "familyMemberNode",
            "position": {"x": 100, "y": 50},
            "data": {
                "id": grandpa_id, "firstName": "John", "lastName": "Doe Sr.", "gender": "male",
                "birthDate": format_date(today - timedelta(days=70*365)),
                "occupation": "Retired Teacher", "bio": "The wise patriarch of the family.",
                "photoUrl": "https://via.placeholder.com/150/771796",
                "conditions": [], "allergies": [], "medications": [],
                "lifestyle": {"smoking": "unknown"}, "vitals": [],
                "customTimelineEvents": [], "sources": [], "isPrivate": False,
            }
        },
        {
            "id": grandma_id,
            "type": "familyMemberNode",
            "position": {"x": 400, "y": 50},
            "data": {
                "id": grandma_id, "firstName": "Jane", "lastName": "Doe (Smith)", "maidenName": "Smith", "gender": "female",
                "birthDate": format_date(today - timedelta(days=68*365)),
                "occupation": "Retired Nurse", "bio": "The loving matriarch, known for her cookies.",
                "photoUrl": "https://via.placeholder.com/150/24f355",
                "conditions": [], "allergies": [], "medications": [],
                "lifestyle": {"smoking": "unknown"}, "vitals": [],
                "customTimelineEvents": [], "sources": [], "isPrivate": False,
            }
        },
        {
            "id": father_id,
            "type": "familyMemberNode",
            "position": {"x": 100, "y": 250},
            "data": {
                "id": father_id, "firstName": "Michael", "lastName": "Doe", "gender": "male",
                "birthDate": format_date(today - timedelta(days=45*365)),
                "occupation": "Engineer", "bio": "Loves tinkering with gadgets.",
                "photoUrl": "https://via.placeholder.com/150/d32776",
                "conditions": [], "allergies": [], "medications": [],
                "lifestyle": {"smoking": "unknown"}, "vitals": [],
                "customTimelineEvents": [], "sources": [], "isPrivate": False,
            }
        },
        {
            "id": mother_id,
            "type": "familyMemberNode",
            "position": {"x": 400, "y": 250},
            "data": {
                "id": mother_id, "firstName": "Sarah", "lastName": "Doe (Johnson)", "maidenName": "Johnson", "gender": "female",
                "birthDate": format_date(today - timedelta(days=43*365)),
                "occupation": "Graphic Designer", "bio": "Creative soul with a passion for art.",
                "photoUrl": "https://via.placeholder.com/150/f66b97",
                "conditions": [], "allergies": [], "medications": [],
                "lifestyle": {"smoking": "unknown"}, "vitals": [],
                "customTimelineEvents": [], "sources": [], "isPrivate": False,
            }
        },
        {
            "id": child1_id, # "You" node
            "type": "familyMemberNode",
            "position": {"x": 100, "y": 450},
            "data": {
                "id": child1_id,
                "firstName": your_name_node_firstname,
                "lastName": your_name_node_lastname,
                "gender": "unknown", 
                "birthDate": format_date(today - timedelta(days=20*365)),
                "occupation": "Student",
                "bio": your_name_node_bio,
                "photoUrl": your_name_node_profile_picture,
                "conditions": [], "allergies": [], "medications": [],
                "lifestyle": {"smoking": "unknown"}, "vitals": [],
                "customTimelineEvents": [], "sources": [], "isPrivate": False,
            }
        },
        {
            "id": child2_id,
            "type": "familyMemberNode",
            "position": {"x": 400, "y": 450},
            "data": {
                "id": child2_id, "firstName": "Alex", "lastName": "Doe", "gender": "male",
                "birthDate": format_date(today - timedelta(days=18*365)),
                "occupation": "Student", "bio": "Your adventurous sibling.",
                "photoUrl": "https://via.placeholder.com/150/b0f7cc",
                "conditions": [], "allergies": [], "medications": [],
                "lifestyle": {"smoking": "unknown"}, "vitals": [],
                "customTimelineEvents": [], "sources": [], "isPrivate": False,
            }
        }
    ]

    default_edges_data = [
        {"id": str(uuid.uuid4()), "source": grandpa_id, "target": grandma_id, "type": "smoothstep", "label": "spouse", "animated": False, "data": {"type": "spouse"}},
        {"id": str(uuid.uuid4()), "source": grandpa_id, "target": father_id, "type": "smoothstep", "label": "parent", "animated": False, "data": {"type": "parent"}},
        {"id": str(uuid.uuid4()), "source": grandma_id, "target": father_id, "type": "smoothstep", "label": "parent", "animated": False, "data": {"type": "parent"}},
        {"id": str(uuid.uuid4()), "source": father_id, "target": mother_id, "type": "smoothstep", "label": "spouse", "animated": False, "data": {"type": "spouse"}},
        {"id": str(uuid.uuid4()), "source": father_id, "target": child1_id, "type": "smoothstep", "label": "parent", "animated": False, "data": {"type": "parent"}},
        {"id": str(uuid.uuid4()), "source": mother_id, "target": child1_id, "type": "smoothstep", "label": "parent", "animated": False, "data": {"type": "parent"}},
        {"id": str(uuid.uuid4()), "source": father_id, "target": child2_id, "type": "smoothstep", "label": "parent", "animated": False, "data": {"type": "parent"}},
        {"id": str(uuid.uuid4()), "source": mother_id, "target": child2_id, "type": "smoothstep", "label": "parent", "animated": False, "data": {"type": "parent"}},
        {"id": str(uuid.uuid4()), "source": child1_id, "target": child2_id, "type": "smoothstep", "label": "sibling", "animated": False, "data": {"type": "sibling"}}
    ]
    
    return {
        "nodes_data": default_nodes_data,
        "edges_data": default_edges_data
    }