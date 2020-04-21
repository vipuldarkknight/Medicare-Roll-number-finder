# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/core/actions/#custom-actions/


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction
from rasa_sdk.forms import FormAction
import requests as req

FACILITY_TYPES = {
    "hospital":
        {
            "name": "hospital",
            "resource": "hospital"
        },
    "medical":
        {
            "name": "Medical College/ Institute",
            "resource": "Medical"
        }
}

base="https://api.data.gov.in/resource/7d208ae4-5d65-47ec-8cb8-2a7a7ac89f8c?api-key=579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b&format=json&offset={}&limit={}"


class FindFacilityTypes(Action):
    """This action class allows to display buttons for each facility type
    for the user to chose from to fill the facility_type entity slot."""

    def name(self) -> Text:
        """Unique identifier of the action"""

        return "find_facility_types"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List:

        buttons = []
        for t in FACILITY_TYPES:
            facility_type = FACILITY_TYPES[t]
            payload = "/inform{\"facility_type\": \"" + facility_type.get(
                "resource") + "\"}"

            buttons.append(
                {"title": "{}".format(facility_type.get("name").title()),
                 "payload": payload})

        # TODO: update rasa core version for configurable `button_type`
        dispatcher.utter_button_template("utter_greet_botdescription", buttons, tracker)
        return []

class FindHealthCareAddress(Action):
    """This action class retrieves the address of the user's
    healthcare facility choice to display it to the user."""

    def name(self) -> Text:
        """Unique identifier of the action"""

        return "find_healthcare_address"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict]:

        facility_type = tracker.get_slot("facility_type")
        healthcare_id = tracker.get_slot("facility_id")
        # print(healthcare_id)
        # healthcare_id = healthcare_id
        
        healthcare_id = int(healthcare_id,10)
        # print(type(healthcare_id))
        bs = base.format(healthcare_id-3,4)
        r=req.get(bs)
        text_json=r.json()
        results = text_json["records"]

        if results:
            global selected
            selected = results[0]
            # print(healthcare_id)
            for res in results:
            	# print(res.get("_sr_no_"))
            	if int(res.get("_sr_no_")) == healthcare_id:
            		# print("---")
            		# print(res.get("_sr_no_"))
            		# print("--")
            		selected = res
            # print(selected.get("_sr_no_"))
            # if facility_type == FACILITY_TYPES["hospital"]["resource"]:
            address = "{}, {}, {} {}".format(selected["address_first_line"].title(),
                                             selected["district"].title(),
                                             selected["state"].upper(),
                                             selected["_pincode"].title())
            return [SlotSet("address", address)]
        else:
            print("No address found. Most likely this action was executed "
                  "before the user choose a healthcare facility from the "
                  "provided list. "
                  "If this is a common problem in your dialogue flow,"
                  "using a form instead for this action might be appropriate.")

            return [SlotSet("address", "not found")]


def _find_facilities(location: Text, resource: Text) -> List[Dict]:
    """Returns json of facilities matching the search criteria."""
    results = []
    # res = resource.split(" ")
    # if len(res)==1:
    # 	resource = resource
    # else:
    # 	resource = res[1]
    print(location)
    # print("========================================")
    print(resource)
    for i in range(104):
    	bs = base.format(10*i,10)
    	r=req.get(bs)
    	text_json=r.json()
    	value = text_json["records"]
    	
    	# print(len(value))	
    	
    	for val in value:
    		if str.isdigit(location):
    			if str(val.get("_pincode")) == location and resource.lower() in val.get("hostipalcaretype").lower():
    				results.append(val)
    		else:
    			# print(val.get("hostipalcaretype").lower())

    			if val.get("state").lower() == location.lower() and resource.lower() in val.get("hostipalcaretype").lower() :
    				# print("1")
    				results.append(val) 
    			elif val.get("district").lower() == location.lower() and resource.lower() in val.get("hostipalcaretype").lower():
    				# print("2")
    				results.append(val)
    			elif val.get("subdristrict").lower() == location.lower() and resource.lower() in val.get("hostipalcaretype").lower():
    				# print("3")
    				results.append(val)
    		if len(results)>=3:
    			break
    	if len(results)>=3:
    		break		
    #print("Full path:")
    #print(full_path)
    # results = requests.get(full_path).json()
    return results


def _resolve_name(facility_types, resource) ->Text:
    for key, value in facility_types.items():
        if value.get("resource") == resource:
            return value.get("name")
    return ""

class Actionfindroll(Action):

    def name(self) -> Text:
        return "action_findroll"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message("Sure i'm on it, 180050119")

        return []


class FacilityForm(FormAction):
    """Custom form action to fill all slots required to find specific type
    of healthcare facilities in a certain city or zip code."""

    def name(self) -> Text:
        """Unique identifier of the form"""

        return "facility_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        return ["facility_type", "location"]

    def slot_mappings(self) -> Dict[Text, Any]:
        return {"facility_type": self.from_entity(entity="facility_type",
                                                  intent=["inform",
                                                          "search_request"]),
                "location": self.from_entity(entity="location",
                                             intent=["inform",
                                                     "search_request"])}

    def submit(self,
               dispatcher: CollectingDispatcher,
               tracker: Tracker,
               domain: Dict[Text, Any]
               ) -> List[Dict]:
        """Once required slots are filled, print buttons for found facilities"""

        location = tracker.get_slot('location')
        facility_type = tracker.get_slot('facility_type')
        # print(location)
        # print("-----------------")
        # print(facility_type)

        results = _find_facilities(location, facility_type)
        # print(len(results))
        # print("******************")
        button_name = _resolve_name(FACILITY_TYPES, facility_type)
        # print(button_name)
        if len(results) == 0:
            dispatcher.utter_message(
                "Sorry, we could not find a {} in {}.".format(button_name,
                                                              location.title()))
            return []

        buttons = []
        # limit number of results to 3 for clear presentation purposes
        for r in results[:3]:
            # if facility_type == FACILITY_TYPES["hospital"]["resource"]:
            facility_id = r.get("_sr_no_")
            name = r["hospitalname"]
            # print(facility_id)
            # print(name)
            # print("|||||||||||||||||||||||")
            # else:
                # facility_id = r["_sr_no_"]
                # name = r["provider_name"]

            payload = "/inform{\"facility_id\":\"" + str(facility_id) + "\"}"
            buttons.append(
                {"title": "{}".format(name.title()), "payload": payload})

        if len(buttons) == 1:
            message = "Here is a {} near you:".format(button_name)
        else:
            # if button_name == "home health agency":
            #     button_name = "home health agencie"
            message = "Here are {} {}s near you:".format(len(buttons),button_name)
            # print(message)

        # TODO: update rasa core version for configurable `button_type`
        # print("yeahhhhhhhhhhhhhhh")
        dispatcher.utter_button_message(message, buttons)
        # print("gooooooooooooooooooo")

        return []
