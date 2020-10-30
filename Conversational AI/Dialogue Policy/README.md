# NgChat Dialogue Policy
## Overview
NgChat Policy is a dialogue management system that can be integrated as a component to Rasa Core. 
### Purpose
The purpose of a dialogue management system is to decide at each moment in the conversation which action the bot should take next. The foundation of Rasa'a dialogue management relies on the TEDPolicy, a transformer model that is trained on conversation 'stories', which contain user intents & entities paired with the desired bot responses and actions. While the TEDPolicy is excellent at handling conversational context and responding to unique dialogues, we find it is too heavy weight and too unpredictable to handle conversations that follow a simple and consistent path. The purpose of NgChat Dialogue policy is to provide an alternative which allows developers to have complete control over the bots response to specified situatations.   
### Implementation
The NgChat Policy is written as a subclass of the Rasa policy class (rasa.core.policies.policy.policy). The policy determines the next action based on a set of hand-written rules which are loaded in from a separate yaml file. These rules are representated as states and the policy itself can be thought of as a finite state machine, where each state has a set of enterance conditions, connections to other states, and a set of actions to execute if the bot enters that state. Most states are enter-states, meaning that they can be entered at any point in the conversation if their conditions are met; others are direct-connect states meaning that they can only be entered if the bot's previous state connects to it. Every time the bot needs to make a decision (usually after a user utterance) the policy evaluates the enterance conditions of each state, calculates a score for each enterable state, and then executes the actions of the highest ranked state. The bot will continue to do this until a listen action is triggered, at which point it will stop to listen to the user's input. 
The score of each state is calcuated as the sum of 4 values: 
 * The number of enterance conditions it has (+1 per)
 * Rank score specified in dialogue.yml (+rank_score, default: 10)
 * If the bot's previous state connects to it (+5)
 * If that connection is a direct connection (+1000)
 
Once a state is selected, the bot will execute all the actions from that state before re-evaluating. If no state's enterance conditions can be met, it will trigger Rasa's DEFAULT_ACTION_FALLBACK followed by a listen action. Similarly, if the confidence level of the user intent is below the NLU threshold, the policy will trigger the fallback.
#### Policy Pseudo-code
```
Upon startup:
Get all intent, entity, and action names from domain
Load dialogue.yml and check validity
Store states as a graph with a dict to access each node -> name2state

# build a graph of states recursively
build_state_graph():
  for state in dialogue.yml:
    build_state_graph_recursively():
      enter_state_dict[state_name] = new state object
      if new state object has connections:
        for each connection build_state_graph_recursively(connection)
# result: a dictionary where the key is the state name and the value is the state object

Prediction:
predict_action_probabilities():
  if there is a chain of actions to be executed: return next action in the chain
  if the NLU confidence < threshold: return fallback
  get_predicted_action():
    for state in name2state:
      get_rank_score():
          Use Rasa tracker and domain to evaluate each state's enterance conditions
          if any condition evaluates false: return 0
          if direct_connection is True but current_state does not connect: return 0
          if direct_connection is true and current_state connects: return 1000
          if direct_connection is false but current_state connects: return 5 + len(conditions)
          else: return len(conditions)
      if highest state score > 0:
        current_state = highest_state
        return highest_state.actions
      else: return None
  if result is not None:
    action_chain = highest_state.actions
    return first item in action chain
  else: return fallback
```
## Rasa Integration
Rasa's dialogue manager (Rasa Core) is built out of components called policies. Every policy is consulted each time the bot needs to make a decision, and each provides a suggested next acion and a confidence score. Rasa Core chooses the policy with the highest confidence, or in case of a tie, the policy with the highest priority. NgChat Dialogue Policy is designed to work as a standalone dialogue manager, meaning that it is not necessary to use any of Rasa's policies. However, it can be used in conjunction with any of Rasa's policies. (TODO: currently ngchat policy always handles fallbacks; introduce parameter that can turn this off so it can be used with other policies). The ngChat Policy always returns a confidence of 1 or 0 and its default priority level is 1.
## Dialogue.yml File
The dialogue.yml file is the set of rules, or states, that the policy will use to make its decisions. Each state is composed of the following key value pairs:
### Dialogue Schema
```
$[state name]: # required formatting, must have a unique name
  direct_connection: bool # optional, default = false
  rank_score: int # optional, default = 10
  conditions: list[Text] # required
    - a list of evaluatable strings
    - can reference certain variables such as SLOTS, INTENT, etc
    - INTENT.name == 'greet'
    - SLOTS.username is not None
  actions: list[Text] # required
    - a list of action names as defined in domain.yml
    - actions will be executed in order and will continue until an action_listen is triggered
    - utter_greet
    - action_greet_user_by_name
    - action_listen
  connections: State # optional, what states are expected to come next
    - $[state name 2]:
        direct_connection: true
        conditions:
          - state2 is true
        actions:
          - action_state_two
```
#### Rank Score
The rank score is used to compute the overall score of each enterable state. The default value is 10, but it can be optionally modified in dialogue.yml to give priority to certain states. 

Example:
`rank_score: 15`
#### Direct Connection
If the state's direct connection is true, and the bot's previous state has a connection to it, the state will get a massive rank score boost so that it is almost guarenteed to be selected if its conditions are met. A use case for this is if you ask the user a yes or no question, the response may not have enough specific detail on its own to know the next action; by knowing the previous context the policy can response to a yes/no answer with high confidence. 

Example:
`direct_connection: true`
#### Conditions
__required__

The conditions are a list of evaluatable python expressions written as strings. The dialogue file has 'access' to certain information from the bot which can be used to evaluate conditions and execute actions. The following are the variables that can be used in the dialogue file to access information about the current state of the bot:
* INTENT: A dict with the most recent INTENT info of the user
     - INTENT.name: The name of the most recent user intent
     - INTENT.confidence: The nlu confidence score
*   ENTITIES: A list of entity names that appeared in the last utterance
*   RESPONSES: A dict of template name/utterance pairs from the domain
     - RESPONSES.greet: A list of utterances available for this template
     - NOTE: Slots will not be filled with current values but will display as shown in domain.yml
*  SLOTS: A dict with slot-name slot-value pairs
     - ex/ SLOTS.store: Starbucks
*   PREV_ACTION: The name of the last action taken by the bot as a string
*   LAST_UTT: The most recent utterance from the bot
*   LAST_ACTION: The most recent action executed by the bot

Example:
```
conditions:
  - INTENT.name == 'greet'
  - SLOTS.name is None
```
#### Actions
__required__

A list of actions to be executed in order by the bot if the state is chosen. These action or utterance names should be exactly as they appear in domain.yml.

Example:
```
actions:
  - 'utter_greet'
  - 'action_ask_name'
  - 'action_listen'
```
#### Connections
Connections represent a chain of dialogue where you expect certain turns from the bot and user to take place in order. The connections attribute is a list of other states, and these connections can expand recursively. A connection gives a small 5 point rank score boost, or a large 1000 point boost if the direct_connection attribute is true.
Example:
```
connections:
  - $[gave name]:
      conditions:
        - SLOTS.name is not None
      actions:
        - 'action_greet_with_name'
```
### Dialogue Example
Here's a small example of a conversation path where the user says 'good morning' and the bot asks if they'd like to hear today's weather.
```
$[good morning]:
  rank_score: 20
  conditions:
    - INTENT.name == 'good_morning'
  actions:
    - utter_good_morning
    - utter_ask_weather
    - action_listen
  connections:
    - $[weather yes]:
        direct_connection: true
        conditions:
          - INTENT.name is 'affirm'
        actions:
          - action_get_weather
        connections:
          - $[got weather]:
              direct_connection: true
              conditions:
                - SLOTS.weather is not None
              actions:
                - utter_weather
                - action_set_weather_to_none
                - action_listen
          - $[get weather fail]:
              direct_connection: true
              conditions:
                - SLOTS.weather is None
              actions:
                - utter_weather_error
                - action_listen
    - $[weather no]:
        direct_connection: true
        conditions:
          - INTENT.name == 'deny'
        actions:
          - utter_no_weather
          - action_listen
```
## How to Use
# Add to config.yml
In order to use the policy with Rasa, you must specify the policy in the configuration file. The only required field is the name, which should be the path to the ngChatPolicy class from your working directory. Additionally, you can specify the location of the dialogue file (default: ./dialogue.yml), and the nlu threshold that determines when the fallback action will be triggered (default: .40). The NgChat Policy can be used as the only policy in the congfig, or it can be used alongside other Rasa policies.
```
policies:
  - name: ngchat_plugins.core.policy.ngchat.ngChatPolicy
    dialogue_path: ./dialogue.yml
    nlu_threshold: .40
```
# Write the Dialogue File
Write the rules/states that will guide the policy to determine the next action at any point in the conversation. Here are some tips and guiding principles to consider when writing the dialogue file:
* Start with states that have a simple 'if this, then do that' behavior and don't rely on previous context; when all the simple states are working, then move on to the more complex states.
* States with very concrete and specific conditions (for example, an intent that always triggers the same response) should have a high priority. Meanwhile, I think of the conversation path that leads towards the end goal as the undercurrent of the conversation; if the user doesn't ask for anything more specific, the bot should default to leading the user to the end goal. 
  * For example, if the purpose of the bot is to get a user to order a coffee, the 'order coffee' path actually has a lower priority than most of the other states. This way, if the user asks for something specific, like seeing the menu or asking an FAQ, the bot will always address that first before heading back to the 'order coffee' path.
* As many states as possible should be available to the user at all times. Similarly, direct connections should be avoided unless necessary.
Direct connections should only be used in cases where entrance to the next state should be guarenteed if the conditions are met and/or if the state conditions cannot be restrictive enough to give admittance at the proper time.
  * For example, the bot asks a yes or no question and the two direct connection states have the conditions 'INTENT.name == affirm' and 'INTENT.name == deny'. These conditions are not clear enough to be on their own, and if one of the conditions is met directly after the previous state, the state should be activated 100% of the time.
* A state should only be entered if its conditions are met, but restrict entrance to the state with its conditions so that it is only entered at the proper time
* NOTE: yaml format does not like to start a value with a quotation mark unless the whole value is quoted (`'action_greet'`: OK | `'item' in ENTITIES`: ERROR). In this case you will have to quote the whole value and then use scare quotes for the substring: ex/ `"'item' in ENTITIES"`
