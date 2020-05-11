# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/core/actions/#custom-actions/


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
import csv

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction, EventType, UserUtteranceReverted, ConversationPaused
from rasa_sdk.forms import FormAction
import requests as req
# from langconv import convtext

from googletrans import Translator
translator = Translator()
translator = Translator(service_urls=[
      'translate.google.com',
      'translate.google.co.kr',
    ])

def convtext(text, src_lang , dest_lang):
    translation = translator.translate(text, dest = dest_lang , src = src_lang)
    # print(translation.text)
    return translation.text

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


INTENT_DESCRIPTION_MAPPING_PATH = "intent_description_mapping.csv"

class ActionDefaultAskAffirmation(Action):
   """Asks for an affirmation of the intent if NLU threshold is not met."""

   def name(self):
       return "action_default_ask_affirmation"

   def __init__(self):
       # self.intent_mappings = {}
       # read the mapping from a csv and store it in a dictionary
       # with open('intent_mapping.csv', encoding='utf-8') as file:
       #     csv_reader = csv.reader(file,delimiter="\t")
       #     for row in csv_reader:
       #          print(row)
       #          self.intent_mappings[row[0]] = row[1]
        import pandas as pd

        self.intent_mappings = pd.read_csv(INTENT_DESCRIPTION_MAPPING_PATH)
        self.intent_mappings.fillna("", inplace=True)

   def run(self, dispatcher, tracker, domain):
        intent_ranking = tracker.latest_message.get("intent_ranking", [])
        if len(intent_ranking) > 1:
            diff_intent_confidence = intent_ranking[0].get("confidence") - intent_ranking[1].get("confidence")
            if diff_intent_confidence < 0.2:
                intent_ranking = intent_ranking[:2]
            else:
                intent_ranking = intent_ranking[:1]

        first_intent_names = [
            intent.get("name", "")
            if intent.get("name", "") not in ["out_of_scope", "chitchat"]
            else tracker.latest_message.get("response_selector")
            .get(intent.get("name", ""))
            .get("full_retrieval_intent")
            for intent in intent_ranking
        ]

        lang = tracker.get_slot("language")
        
        if lang =="hindi":
            message_title = "क्षमा करें, मुझे यकीन नहीं है कि मैंने आपको सही ढंग से समझा है 🤔 क्या आपका मतलब है..."
        else:
            message_title = "Sorry, I'm not sure I've understood you correctly 🤔 Do you mean..."
        buttons = []
        for intent in first_intent_names:
            button_title = self.get_button_title(intent)
            if "/" in intent:
                # here we use the button title as the payload as well, because you
                # can't force a response selector sub intent, so we need NLU to parse
                # that correctly
                if lang =="hindi":
                    button_title = convtext(button_title , 'en' , 'hi')
                buttons.append({"title": button_title, "payload": button_title})
            else:
                if lang =="hindi":
                    button_title = convtext(button_title , 'en' , 'hi')
                buttons.append(
                    {"title": button_title, "payload": f"/{intent}"}
                )

        if lang =="hindi":
            buttons.append({"title": "कुछ और", "payload": "/trigger_rephrase_hi"})
        else:
            buttons.append({"title": "Something else", "payload": "/trigger_rephrase"})

        dispatcher.utter_message(text=message_title, buttons=buttons)
       # get the most likely intent
       # last_intent_name = tracker.latest_message['intent']['name']

       # get the prompt for the intent
       # intent_prompt = self.intent_mappings[last_intent_name]

       # Create the affirmation message and add two buttons to it.
       # Use '/<intent_name>' as payload to directly trigger '<intent_name>'
       # when the button is clicked.
       # message = "Did you mean '{}'?".format(intent_prompt)
       # buttons = [{'title': 'Yes',
       #             'payload': '/{}'.format(last_intent_name)},
       #            {'title': 'No',
       #             'payload': '/out_of_scope/other'}]
       # dispatcher.utter_message(text = message, buttons=buttons)

        return []

   def get_button_title(self, intent: Text) -> Text:
        default_utterance_query = self.intent_mappings.intent == intent
        utterance_query = (
            default_utterance_query
        )

        utterances = self.intent_mappings[utterance_query].button.tolist()

        if len(utterances) > 0:
            button_title = utterances[0]
        else:
            utterances = self.intent_mappings[default_utterance_query].button.tolist()
            button_title = utterances[0] if len(utterances) > 0 else intent

        return button_title

class ActionDefaultFallback(Action):
    def name(self) -> Text:
        return "action_default_fallback"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[EventType]:

        # Fallback caused by TwoStageFallbackPolicy
        lang = tracker.get_slot("language")
        if (
            len(tracker.events) >= 4
            and tracker.events[-4].get("name") == "action_default_ask_affirmation"
        ):

            dispatcher.utter_message(template="utter_restart_with_button")

            return [SlotSet("feedback_value", "negative"), ConversationPaused()]

        # Fallback caused by Core
        else:
            if lang=="hindi":
                dispatcher.utter_message(template="utter_default_hi")
            else:
                dispatcher.utter_message(template="utter_default")
            return [UserUtteranceReverted()]

class FindLanguageType(Action):
    """This action class allows to display buttons for each facility type
    for the user to chose from to fill the facility_type entity slot."""

    def name(self) -> Text:
        """Unique identifier of the action"""

        return "find_language_type"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List:

        buttons = []
        # for t in FACILITY_TYPES:
            # facility_type = FACILITY_TYPES[t]
        payload1 = "/inform{\"language\": \"" + "hindi" + "\"}"
        payload2 = "/inform{\"language\": \"" + "english" + "\"}"

        buttons.append(
            {"title": "{}".format("Hindi"),
             "payload": payload1})
        buttons.append(
            {"title": "{}".format("English"),
             "payload": payload2})

        # TODO: update rasa core version for configurable `button_type`
        dispatcher.utter_message(text="Please choose your Preferred language/कृपया अपनी पसंदीदा भाषा चुनें", buttons=buttons)
        return []

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

        lang = tracker.get_slot("language")
        # print(lang)
        
        buttons = []
        if lang=="hindi":
        	for t in FACILITY_TYPES:
        		facility_type = FACILITY_TYPES[t]
        		payload = "/inform{\"facility_type\": \"" + facility_type.get("resource") + "\"}"
        		buttons.append({"title": "{}".format(convtext(facility_type.get("name").title() , 'en' , 'hi' )),"payload": payload})
        	dispatcher.utter_message(template="utter_greet_botdescription_hi",buttons=buttons)
        else:
	        for t in FACILITY_TYPES:
	            facility_type = FACILITY_TYPES[t]
	            payload = "/inform{\"facility_type\": \"" + facility_type.get(
	                "resource") + "\"}"

	            buttons.append(
	                {"title": "{}".format(facility_type.get("name").title()),
	                 "payload": payload})
	        dispatcher.utter_message(template="utter_greet_botdescription",buttons=buttons)

        # TODO: update rasa core version for configurable `button_type`
        
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

class Actionasklocation(Action):

    def name(self) -> Text:
        return "action_ask_location"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        lang = tracker.get_slot("language")
        if lang=="hindi":
            dispatcher.utter_message(template="utter_ask_loc_hi")
        else:
            dispatcher.utter_message(template="utter_ask_loc")

        return []

class Actionsayaddress(Action):

    def name(self) -> Text:
        return "action_say_address"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        lang = tracker.get_slot("language")
        if lang=="hindi":
            dispatcher.utter_message(template="utter_address_hi")
        else:
            dispatcher.utter_message(template="utter_address")

        return []

class Actionanythingelse(Action):

    def name(self) -> Text:
        return "action_anything_else"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        lang = tracker.get_slot("language")
        if lang=="hindi":
            dispatcher.utter_message(template="utter_anything_else_hi")
        else:
            dispatcher.utter_message(template="utter_anything_else")

        return []

class Actionaskfeedback(Action):

    def name(self) -> Text:
        return "action_ask_feedback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        lang = tracker.get_slot("language")
        if lang=="hindi":
            dispatcher.utter_message(template="utter_ask_feedback_hi")
        else:
            dispatcher.utter_message(template="utter_ask_feedback")

        return []

class Actiongreat(Action):

    def name(self) -> Text:
        return "action_great"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        lang = tracker.get_slot("language")
        if lang=="hindi":
            dispatcher.utter_message(template="utter_great_hi")
        else:
            dispatcher.utter_message(template="utter_great")

        return []

class Actiongoodbye(Action):

    def name(self) -> Text:
        return "action_goodbye"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        lang = tracker.get_slot("language")
        if lang=="hindi":
            dispatcher.utter_message(template="utter_goodbye_hi")
        else:
            dispatcher.utter_message(template="utter_goodbye")

        return []

class Actionwhathelp(Action):

    def name(self) -> Text:
        return "action_what_help"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        lang = tracker.get_slot("language")
        if lang=="hindi":
            dispatcher.utter_message(template="utter_what_help_hi")
        else:
            dispatcher.utter_message(template="utter_what_help")

        return []

class Actioncontactemail(Action):

    def name(self) -> Text:
        return "action_contact_email"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        lang = tracker.get_slot("language")
        if lang=="hindi":
            dispatcher.utter_message(template="utter_contact_email_hi")
        else:
            dispatcher.utter_message(template="utter_contact_email")

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
        
        lang = tracker.get_slot("language")
        if lang=="hindi":
        	location = convtext(location , 'hi' , 'en')
        	facility_type = convtext(facility_type , 'hi' , 'en')
        

        results = _find_facilities(location, facility_type)
        print(location)
        print(facility_type)
        print("-----")
        button_name = _resolve_name(FACILITY_TYPES, facility_type)
        print(button_name)
        # print(button_name)
        if len(results) == 0:
        	if lang=="hindi":
        		dispatcher.utter_message(text = "क्षमा करें, हम {} के अंदर एक {} नहीं पा सके.".format(location.title(),button_name))
        	else:
        		dispatcher.utter_message(text = "Sorry, we could not find a {} in {}.".format(button_name,location.title()))
        	return []


        buttons = []
        # limit number of results to 3 for clear presentation purposes
        for r in results[:3]:
            # if facility_type == FACILITY_TYPES["hospital"]["resource"]:
            facility_id = r.get("_sr_no_")
            name = r["hospitalname"]

            payload = "/inform{\"facility_id\":\"" + str(facility_id) + "\"}"
            buttons.append(
                {"title": "{}".format(name.title()), "payload": payload})

        if len(buttons) == 1:
            if lang=="hindi":
            	message = "यहाँ आप के पास एक {} है:".format(button_name)
            else:
            	message = "Here is a {} near you:".format(button_name)
        else:
            # if button_name == "home health agency":
            #     button_name = "home health agencie"
            if lang=="hindi":
                print(button_name)
                message = "यहाँ आप के पास {} {} हैं:".format(len(buttons),button_name)
            else:
            	message = "Here are {} {}s near you:".format(len(buttons),button_name)

            # print(message)

        # TODO: update rasa core version for configurable `button_type`
        
        dispatcher.utter_message(text = message, buttons = buttons)
        

        return []



# def tag_convo(tracker: Tracker, label: Text) -> None:
#     """Tag a conversation in Rasa X with a given label"""
#     endpoint = f"http://{config.rasa_x_host}/api/conversations/{tracker.sender_id}/tags"
#     requests.post(url=endpoint, data=label)
#     return

# class ActionTagFeedback(Action):
#     """Tag a conversation in Rasa X as positive or negative feedback """

#     def name(self):
#         return "action_tag_feedback"

#     def run(self, dispatcher, tracker, domain) -> List[EventType]:

#         feedback = tracker.get_slot("feedback_value")

#         if feedback == "positive":
#             label = '[{"value":"postive feedback","color":"76af3d"}]'
#         elif feedback == "negative":
#             label = '[{"value":"negative feedback","color":"ff0000"}]'
#         else:
#             return []

#         tag_convo(tracker, label)

#         return []



# --------------------------------------------------------------------------------------------------------------------------- 
# ---------------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------





# class ActionGreetUser(Action):
#     """Greets the user with/without privacy policy"""

#     def name(self) -> Text:
#         return "action_greet_user"

#     def run(self, dispatcher, tracker, domain) -> List[EventType]:
#         intent = tracker.latest_message["intent"].get("name")
#         print(intent)
#         if intent=="greet":
#           lang = tracker.get_slot("language")
#           # dispatcher.utter_message(template="find_facility_types")
#           buttons = []
#           if lang=="hindi":
#               for t in FACILITY_TYPES:
#                   facility_type = FACILITY_TYPES[t]
#                   payload = "/inform{\"facility_type\": \"" + facility_type.get("resource") + "\"}"
#                   buttons.append({"title": "{}".format(convtext(facility_type.get("name").title() , 'en' , 'hi' )),"payload": payload})
#               dispatcher.utter_button_template("utter_greet_botdescription_hi", buttons, tracker)
#           else:
#               for t in FACILITY_TYPES:
#                   facility_type = FACILITY_TYPES[t]
#                   payload = "/inform{\"facility_type\": \"" + facility_type.get(
#                       "resource") + "\"}"

#                   buttons.append(
#                       {"title": "{}".format(facility_type.get("name").title()),
#                        "payload": payload})
#               dispatcher.utter_button_template("utter_greet_botdescription", buttons, tracker)
#           # return []
            
#         else:
#             # dispatcher.utter_message(template="find_language_type")
#             buttons = []
#             payload1 = "/inform{\"language\": \"" + "Hindi" + "\"}"
#             payload2 = "/inform{\"language\": \"" + "English" + "\"}"
#             buttons.append({"title": "{}".format("hindi"), "payload": payload1})
#             buttons.append({"title": "{}".format("english"), "payload": payload2})
#             dispatcher.utter_button_template("Please choose your Preferred language", buttons, tracker)
#         return []