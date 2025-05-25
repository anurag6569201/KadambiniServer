from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
import json


def transform_family_data(input_dict_data):
    """
    Transforms the input family tree data (as a Python dictionary)
    into the desired output format (as a Python dictionary).
    Args:
        input_dict_data: A Python dictionary containing the input family tree data.
                         Expected to have 'nodes' and 'edges' keys.
    Returns:
        A Python dictionary containing the transformed data.
    """
    output_data = {
        "members": [],
        "relationships": [],
        "theme": "light" 
    }

    for node in input_dict_data.get("nodes", []): 
        member_data = node.get("data", {}).copy() 
        member_data["position"] = node.get("position")
        
        if "id" not in member_data and "id" in node:
            member_data["id"] = node["id"]
        output_data["members"].append(member_data)

    for edge in input_dict_data.get("edges", []): 
        relationship_data = edge.get("data", {}).copy()
        if "id" not in relationship_data and "id" in edge:
            relationship_data["id"] = edge["id"]
        output_data["relationships"].append(relationship_data)
        
    return output_data 