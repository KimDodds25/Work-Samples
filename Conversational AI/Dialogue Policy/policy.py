"""Custom rule-based policy for rasa core using ngChatDialogue.

Rasa allows the use of custom policies for next-action-prediction.
Rasa's TEDPolicy is a great machine learning approach, but we feel it is
too heavy-weight for something like a coffee bot, and we find the forms to
be too-restrictive for the purposes of ordering. ngChatPolicy is a
rule-based dialogue manager that reads in and parses a YAML file to find the correct
conversation path and next action.
"""
import os
import json
import yaml
import logging
from addict import Dict as adDict
from typing import Any, List, Text, Optional, Dict, Tuple, Set

import rasa.utils.io
from rasa.core.domain import Domain
from rasa.core.policies.policy import Policy
from rasa.core.interpreter import NaturalLanguageInterpreter, RegexInterpreter
from rasa.core.trackers import DialogueStateTracker
from rasa.core.constants import DEFAULT_POLICY_PRIORITY
from rasa.core.actions.action import ACTION_DEFAULT_FALLBACK_NAME
from rasa.core.actions.action import ACTION_LISTEN_NAME


logger = logging.getLogger(__name__)
DEFAULT_DIALOG_PATH = './dialogue.yml'
DEFAULT_NLU_THRESHOLD = .40
DEFAULT_RANK_SCORE = 10


class ngChatPolicy(Policy):
    """Custom rule-based policy class for rasa.

    This policy creates a tree with possible conversation paths
    based on a dialogue.yml file. If there is a valid action based
    on the rules and the current tracker state, the policy returns
    the predicted action with a probability of 1. If not valid action
    is found, the policy returns an empty array.

    Attributes:
        dialogue_path (Text): The path to the dialogue.yml file
        action_chain (List[Text]): A list of actions to be executed
            in order with full confidence
        dialogue_tree (DialogTree): A dialogue tree built from the user-provided
            rules in dialogue.yml

    """

    @staticmethod
    def _standard_featurizer() -> None:
        """No featurizer used."""
        return None

    def __init__(
        self,
        priority: int = DEFAULT_POLICY_PRIORITY,
        dialogue_path: Text = DEFAULT_DIALOG_PATH,
        nlu_threshold: float = DEFAULT_NLU_THRESHOLD,
        action_chain: List[Text] = [],
        enter_states: Dict[Text, 'StateNode'] = {},
        current_state: Optional['StateNode'] = None,
        domain_action_names: List[Text] = [],
        domain_responses: Dict[Text, List[Dict[Text, Any]]] = {}
    ) -> None:
        """Initialize policy with any arguments in config.yml.

        Args:
            priority (int): priority level of policy, set in config.yml

        """
        super().__init__(priority=priority)
        self.dialogue_path = dialogue_path
        self.nlu_threshold = nlu_threshold
        self.domain_action_names = set(domain_action_names)
        self.domain_responses = domain_responses
        self.action_chain = []
        self.name2state = StateNode.build_graph(self.dialogue_path, self.domain_action_names)
        self.current_state = None

    def train(
        self,
        training_trackers: List[DialogueStateTracker],
        domain: Domain,
        interpreter: NaturalLanguageInterpreter = None,
        **kwargs: Any,
    ) -> None:
        """Get domain action names."""
        self.domain_action_names = set(domain.action_names)
        self.domain_responses = domain.templates
        if not self.domain_action_names:
            logger.error("There was an error loading the actions from domain")
        logger.info(f"Checking {self.dialogue_path} file")
        StateNode.build_graph(self.dialogue_path, self.domain_action_names)
        return

    def predict_action_probabilities(
        self,
        tracker: DialogueStateTracker,
        domain: Domain,
        interpreter: NaturalLanguageInterpreter = RegexInterpreter(),
        **kwargs: Any,
    ) -> List[float]:
        """Predict the next action the bot should take after seeing the tracker.

        Args:
            tracker: the class `rasa.core.trackers.DialogueStateTracker`
            domain: the class `rasa.core.domain.Domain`
            interpreter: Interpreter which may be used by the policies to create
                additional features.
        Returns:
             List[float]: the list of probabilities for the next actions, where each action has
                an index and the number in the index corresponds to the probability of that action being predicted

        """
        # check if there is an active action chain
        if self.action_chain:
            logger.debug(f"Action chain: {self.action_chain}")
            return self.confidence_scores(domain)

        # check if NLU confidence is above threshold
        confidence = tracker.latest_message.intent.get('confidence')
        if confidence is not None and confidence < self.nlu_threshold:
            self.action_chain = [ACTION_DEFAULT_FALLBACK_NAME, ACTION_LISTEN_NAME]
            logger.info(f"Intent confidence {confidence} below NLU threshold {self.nlu_threshold}, returning fallback")
            return self.confidence_scores(domain)

        # traverse tree to get best next action
        # if there is a valid action, add the result to the action_chain,
        # pop the first action and return it
        self.action_chain = self.get_predicted_action(tracker)
        if self.action_chain:
            logger.debug(f"Action chain: {self.action_chain}")
        # if no valid action is found, return fallback
        else:
            self.action_chain = [ACTION_DEFAULT_FALLBACK_NAME, ACTION_LISTEN_NAME]

        return self.confidence_scores(domain)

    def get_predicted_action(self, tracker: DialogueStateTracker) -> Optional[List[Text]]:
        """Traverse the dialogue tree to find the best next action.

        Traverse tree to find all valid states. The state with the most conditions takes
        precedence. In the case of a tie, the state with a higher rank score is chosen.
        If there is still a tie, chose randomly from the best states. If there is no
        valid state, return None.

        Args:
            tracker: rasa DialogueStateTracker

        Return:
            Optional[List[Text]]: A list of actions to be executed in order, or none if there
                is no valid state

        """
        score_state_list = []
        curr_state_conn = self.current_state.connections if self.current_state else []
        logger.debug(f"Current state connections: {[conn.name for conn in curr_state_conn]}")
        for state in self.name2state.values():
            score_state_list.append((state.can_pass(tracker, self.domain_responses, curr_state_conn), state))

        if score_state_list:
            sorted_score_state = sorted(score_state_list, key=lambda x: x[0], reverse=True)
            best_score_state = sorted_score_state[0]
            logger.debug(f"Top 5 states: {sorted_score_state[:5]}")
            logger.info(f"Best state: {best_score_state}")

            if best_score_state[0] > 0:
                self.current_state = best_score_state[1]
                logger.debug(f"current_state: {self.current_state}")
                logger.debug(f"Returning the following actions: {best_score_state[1].actions}")
                return best_score_state[1].actions.copy()
            else:
                self.current_state = None
                logger.debug("current_state: None")
        return None

    def confidence_scores(self, domain: Domain) -> List[float]:
        """Return confidence scores if a single action is predicted.

        Args:
            action_name: the name of the action for which the score should be set
            value: the confidence for `action_name`
            domain: the :class:`rasa.core.domain.Domain`
        Returns:
            the list of the length of the number of actions

        """
        results = [0.0] * domain.num_actions
        idx = domain.index_for_action(self.action_chain.pop(0))
        results[idx] = 1.0
        return results

    def persist(self, path: Text) -> None:
        """Persist the policy to a storage.

        Args:
            path: the path where to save the policy to

        """
        config_file = os.path.join(path, "ngchat_dialogue_policy.json")
        meta = {
            "priority": self.priority,
            "action_chain": self.action_chain,
            "current_state": self.current_state,
            "domain_action_names": list(self.domain_action_names),
            "domain_responses": self.domain_responses,
            "nlu_threshold": self.nlu_threshold,
        }
        rasa.utils.io.create_directory_for_file(config_file)
        rasa.utils.io.dump_obj_as_json_to_file(config_file, meta)

    @classmethod
    def load(cls, path: Text) -> "ngChatPolicy":
        """Load a policy from the storage.

        Args:
            path (Text): the path from where to load the policy

        """
        meta = {}
        if os.path.exists(path):
            meta_path = os.path.join(path, "ngchat_dialogue_policy.json")
            if os.path.isfile(meta_path):
                meta = json.loads(rasa.utils.io.read_file(meta_path))

        return cls(**meta)

    @staticmethod
    def _default_predictions(domain: Domain) -> List[float]:
        """Create a list of zeros.

        Args:
            domain: the :class:`rasa.core.domain.Domain`
        Returns:
            the list of the length of the number of actions

        """
        return [0.0] * domain.num_actions


class StateNode:
    """Store information about a state. Nodes are used to create a dialogue tree.

    Attributes:
        state_name (Text): The name of the state, defined in dialogue.yml
        conditions (List[Text]): A list of readable conditions that must be met
            in order to enter the node. (ex/ '![item] != None')
        actions (List[Text]): A list of action names to be executed in order if
            the node is chosen
        connections (List[StateNode]): Subordinate state nodes
        rank_score (int): A score to be used in case of ties between states

    """

    def __init__(self, name: Text = '', conditions: List[Text] = [],
                 actions: List[Text] = [], direct_con: bool = False,
                 connections: List['StateNode'] = [], score: float = 10) -> None:
        """Initialize a state node with name, conditions, actions, connections, and score."""
        self.name = name
        self.direct_connection = direct_con
        self.conditions = conditions
        self.actions = actions
        self.connections = connections
        self.rank_score = score

    @classmethod
    def from_data(cls, name: Text, state_data: Dict[Text, Any], domain_actions: Set[Text]) -> 'StateNode':
        """Validate information from dialogue.yml before creating node object.

        Args:
            name: name of the state
            state_data: A dict containing all the info for the state
            domain_actions: A list of action names that are valid in the domain

        Returns:
            StateNode: class object

        """
        if not name:
            raise yaml.YAMLError("Invalid dialogue yaml file: missing state name in dialogue.yml")

        for key in state_data.keys():
            if key not in ['conditions', 'actions', 'connections', 'direct_connection', 'rank_score']:
                raise yaml.YAMLError(f"There is a key error in state {name}: {key}")

        direct_con = state_data.get('direct_connection', False)
        if type(direct_con) is not bool:
            raise yaml.YAMLError(f"Error in state {name}: The value of direct_connection must be a bool")

        try:
            score = state_data.get('rank_score', DEFAULT_RANK_SCORE)
        except ValueError:
            raise yaml.YAMLError(f"Error in state {name}: Value of rank_score must be an int or float")

        conditions = state_data.get('conditions', [])
        StateNode.check_conditions(name, conditions)

        actions = state_data.get('actions', [])
        StateNode.check_actions(name, actions, domain_actions)

        connections = state_data.get('connections', [])
        return cls(name, conditions, actions, direct_con, connections, score)

    @staticmethod
    def check_conditions(name: Text, conditions: Any) -> None:
        """Check node conditions and throw exceptions if errors found.

        Args:
            name: name of the state
            conditions: The conditions section of the state information

        """
        if not conditions:
            logger.warn(f"The state {name} does not have any entrance conditions")
        if type(conditions) != list:
            raise yaml.YAMLError("Error in state {name}: The value of conditions must be a list")
        for condition in conditions:
            for reserved in ['keys', 'values', 'items']:
                if f".{reserved}" in condition:
                    logger.warn(f"Did you use Dict.{reserved} to access Dict? 'keys', 'values', and 'items'"
                                " are reserved keywords, please use Dict['{reserved}']")
        return

    @staticmethod
    def check_actions(name: Text, actions: Any, domain_actions: Set[Text]) -> None:
        """Check node actions and throw exceptions if errors found.

        Args:
            name: name of the state
            actions: The actions section of the node information
            domain_actions: A list of valid action names from the domain

        """
        if not actions:
            raise yaml.YAMLError(f'Invalid dialogue yaml file: "{name}" does not specify any actions to execute')
        if type(actions) is not list:
            raise yaml.YAMLError("Error in state {name}: The value of actions must be a list")
        if domain_actions:
            for action in actions:
                if action not in domain_actions:
                    raise yaml.YAMLError(f"Error in state {name}: {action} is not a valid action in the domain")
        return

    # Did I do something wrong here? This isn't working
    def __str__(self) -> Text:
        """Print StateNodes as just the name."""
        return f"{self.name}"

    def __repr__(self) -> Text:
        """Print StateNodes as just the name."""
        return f"{self.name}"

    @staticmethod
    def build_graph(path: Text, domain_actions: Set[Text]) -> Dict[Text, 'StateNode']:
        """Build a dialogue graph given a dialogue.yml file.

        Args:
            path (Text): The path to the dialogue.yml file
            domain_actions (List[Text]): List of actions in Rasa domain

        Return:
            Dict[Text, StateNode]: A dict of enter nodes

        """
        states = None
        name2state = {}
        with open(path, 'r') as fin:
            try:
                states = yaml.safe_load(fin)
            except yaml.YAMLError as e:
                logger.error(e)
        # Recursively build the tree and store each enter node in root.connections
        if states:
            for s in states.keys():
                name2state.update(StateNode.build_graph_rec(s, states.get(s), {}, domain_actions)[0])
        return name2state

    @staticmethod
    def build_graph_rec(state_name: Text, state: Dict[Text, Any], state_dict: Dict[Text, 'StateNode'],
                        domain_actions: Set[Text]) -> Optional[Tuple[Dict[Text, 'StateNode'], 'StateNode']]:
        """Build graph recursively, where a StateNode can have subordinate StateNodes in its connections.

        Args:
            state_name (Text): The name of the state as defined in dialogue.yml
            state (Dict[Text, Any]): The information about the state - conditions, actions, connections, etc
            state_dict (Dict[Text, 'StateNode']): A dict that holds each created StateNode
            domain_actions (List[Text]): A list containing all the valid actions in the domain

        Return:
            Dict[Text, StateNode]: A dictionary containing all the state node

        """
        # if the node does not have any connections, it is an end vertex; return a StateNode
        if not state.get('connections'):
            new_node = StateNode.from_data(name=state_name, state_data=state, domain_actions=domain_actions)
            state_dict[state_name] = new_node
            return (state_dict, new_node)
        # else, descend recursively until hitting an end vertex, then build nodes on the way up
        else:
            connection_objects = []
            for connection in state.get('connections', []):
                for name in connection.keys():
                    dict_node = StateNode.build_graph_rec(name, connection.get(name), {}, domain_actions)
                    if dict_node:
                        connection_objects.append(dict_node[1])
                        state_dict.update(dict_node[0])
                if state_name in state_dict.keys():
                    raise yaml.YAMLError(f'Duplicate state ID "{state_name}" in dialogue file')
            state['connections'] = connection_objects
            new_node = StateNode.from_data(name=state_name, state_data=state, domain_actions=domain_actions)
            state_dict[state_name] = new_node
            return (state_dict, new_node)

    def can_pass(self, tracker: DialogueStateTracker, domain_responses: Dict[Text, List],
                 curr_state_connections: List['StateNode']) -> float:
        """Evaluate the truth of a state based on its list of conditions.

        Each state has a list of readable conditions (ex/ '![item] != None') that must
        be met in order to enter the state. All conditions must be met to be true.

        Args:
            tracker: rasa DialogueStateTracker

        Return:
            float: rank score if all conditions are met, 0 otherwise

        """
        # A dict with the keys 'name' and 'confidence' for the most recent intent
        INTENT = adDict(tracker.latest_message.intent)  # noqa: F841
        # A list of dicts where each item in the list is a dict of information on one extracted
        # entity from the previous user utterence. Keys: 'entity', 'start', 'end', 'extractor', 'value'
        ENTITIES = [entity['entity'] for entity in tracker.latest_message.entities]  # noqa: F841
        # A dict of slot-name, slot-value pairs
        SLOTS = adDict(tracker.current_slot_values())  # noqa: F841
        # A dict of response template names and utterances
        responses = {}
        for key in domain_responses.keys():
            responses[key] = [value['text'] for value in domain_responses[key]]
        RESPONSES = adDict(responses)  # noqa: F841
        # A string containing the name of the most recently executed action
        PREV_ACTION = tracker.latest_action_name  # noqa: F841
        # A string containing the name of the most recent utterance said by the bot
        LAST_UTT = tracker.latest_bot_utterance  # noqa: F841
        # A string of the last action performed by the bot
        LAST_ACTION = tracker.latest_action_name  # noqa: F841

        overall_score = self.rank_score + len(self.conditions)

        # check all conditions and immediately return 0 if any fail
        for condition in self.conditions:
            try:
                if not eval(condition):
                    # logger.debug(f"State {self.name} failed on condition: {condition}")
                    return 0
            except Exception as e:
                logger.error(f"The condition '{condition}' could not be evaluated: {e}")
                return 0

        # if one of current state's connections is direct connect, prioritize it
        if self.direct_connection is True:
            if self in curr_state_connections:
                return 1000
            else:
                # logger.debug(f"State {self.name} failed, direct connection not valid")
                return 0

        # if current state has a connection but it's not a direct connect, give slight score bump
        if self in curr_state_connections and self.direct_connection is False:
            overall_score += 5

        return overall_score
