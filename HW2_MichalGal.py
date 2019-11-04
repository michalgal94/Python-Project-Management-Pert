import logging

logging.basicConfig(filename='graph_logger.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Activity:
    def __init__(self, name, duration):
        self.name = name
        self.duration = duration
        logging.info("New activity: name:" + str(name) + ", duration: " + str(duration))

    '''
    Question #6 - Overwriting __str__ method
    '''
    def __str__(self):
        res = "Activity Name: " + self.name + ", Duration: " + str(self.duration)
        logging.info("str was used from '" + self.name + "' activity")
        return res

    def __repr__(self):
        # logging.info("repr was used from '" + self.name + "' activity") # making the logging process INconvenience
        return self.name

    def __eq__(self, other):
        # logging.info("eq was used from '" + self.name + "' activity") # making the logging process INconvenience
        return self.name == other.name and self.duration == other.duration

    def __hash__(self):
        # logging.info("hash was used from '" + self.name + "' activity") # making the logging process INconvenience
        key_tuple = (self.name, self.duration)
        return hash(key_tuple)


class Graph:
    def __init__(self, graph={}):
        self.outward_dict = graph
        self.inward_dict = {}
        self.slack_dict = {}
        self.start = Activity
        self.finish = Activity
        if len(self.outward_dict) > 0:
            self.set_graph()
        logging.info("New graph created: " + str(graph))

    '''
    Question #6 - Overwriting __str__ method
    '''
    def __str__(self):
        iterator = iter(self)
        graph_str = "Activities:\n"
        for activity in iterator:
            graph_str += str(activity) + "\n"
        logging.info("str was used from '" + repr(self) + "' graph")
        if len(self.outward_dict) > 0:
            return (graph_str + "Connections:\n"
                + "outwards:\t" + str(self.outward_dict)
                + "\nInwards:\t" + str(self.inward_dict)
                + "\nTotal duration: "
                + str(self.slack_dict[self.finish]["ef"]))
        else: return "empty graph"

    '''
    Question #7 - iterator for "pert" class (Graph class)
    '''
    def __iter__(self):
        logging.info("iterator for '" + repr(self) + "' graph")
        return iter(self.outward_dict)

    '''
    Initialize the graph from a given representation of a graph.
    Set the inward_dict from the outward_dict, and calculate its slack values.
    '''
    def set_graph(self):
        for activity in self.outward_dict:
            self.inward_dict[activity] = []
        for activity in self.outward_dict:
            if activity.name == "start":
                self.start = activity
            if activity.name == "finish":
                self.finish = activity
            for i in self.outward_dict[activity]:
                self.inward_dict[i].append(activity)
        self.calc_slack_vars()
        logging.info("The graph: \n" + str(self) + "\nhas been set")

    '''
    Question #2 - method to add an activity to the project.
    need to insert the inward connections and outward connections (empty list as default),
        and calculate new slack values.
    '''
    def add_activity(self, activity, inward=[], outward=[]):
        if activity not in self.outward_dict:
            self.outward_dict[activity] = outward
            for node in inward:
                self.outward_dict[node].append(activity)
            self.inward_dict[activity] = inward
            for node in outward:
                self.inward_dict[node].append(activity)
            self.calc_slack_vars()
        logging.info("'add_activity' method used to add " + str(activity))

    '''
    Question #3 - method to find isolated activities.
        checking if there's an outward connection and then if there's also an inward connection.
    '''
    def isolated_activities(self):
        is_isolated = []
        isolated = []
        for activity in self.outward_dict:
            if self.outward_dict[activity] == list():
                is_isolated.append(activity)
        for activity in self.inward_dict:
            if self.inward_dict[activity] == list():
                if activity in is_isolated:
                    isolated.append(activity)
        logging.info("'isolated_activities' was used from graph: " + repr(self))
        return isolated

    '''
    creating the structure of slack_dict property.
    '''
    def reset_slacks(self):
        for activity in self.outward_dict:
            self.slack_dict[activity] = {"es": 0, "ef": 0, "ls": 0, "lf": 0, "slack": 0, "duration": activity.duration}
            if activity.name == "start":
                self.slack_dict[activity]["ef"] = activity.duration
        logging.info("'reset_slacks' was called")

    '''
    remove isolated activities from slack_dict to prevent them from being with zero value in slack.
    used in 'calc_slack_vars' method
    '''
    def remove_isolated_from_slacks(self):
        isolated = self.isolated_activities()
        for activity in self.outward_dict:
            if activity in isolated:
                self.slack_dict.__delitem__(activity)
        logging.info("'remove_isolated_from_slacks' was called")

    ''''
    return a list of activities that connect to the <param> last_activity <param> activity,
        without considering sub-activities even if connected to finish. 
    used in 'calc_slack_vars' method.
    '''
    def get_next_stage_from_finish(self, last_activity):
        finishers = self.inward_dict[last_activity]
        for activity in self.inward_dict:
            if activity in finishers:
                for node in self.inward_dict[activity]:
                    if node in finishers:
                        finishers.remove(node)
        logging.info("'get_next_stage_from_finish' was called")
        return finishers

    ''''
    updates the slack_dict attribute of the graph -
    inserting all es, ef, ls, lf and slack variables of all activities.
    doing so by first inserting all es, ef values in a simple loop,
        next inserting finish activity ls and lf.
        next inserting all activities'es ls and lf values using the get_next_stage_from_finish method to find out
            what goes where.
    '''
    def calc_slack_vars(self, reset = 0):
        if reset == 0:
            self.reset_slacks()
            self.remove_isolated_from_slacks()
        self.slack_dict[self.start]["ef"] = self.slack_dict[self.start]["duration"]
        # self.slack_dict[self.start]["ef"] = self.start.duration
        for activity in self.outward_dict:
            for node in self.outward_dict[activity]:
                if self.slack_dict[activity]["ef"] > self.slack_dict[node]["es"] or self.slack_dict[node]["ef"] == 0:
                    self.slack_dict[node]["es"] = self.slack_dict[activity]["ef"]
                    self.slack_dict[node]["ef"] = self.slack_dict[node]["es"] + self.slack_dict[node]["duration"]
        self.slack_dict[self.finish]["lf"] = self.slack_dict[self.finish]["ef"]
        self.slack_dict[self.finish]["ls"] = self.slack_dict[self.finish]["lf"] - self.slack_dict[self.finish]["duration"]
        # self.slack_dict[self.finish]["ls"] = self.slack_dict[self.finish]["lf"] - self.finish.duration
        finishers = self.get_next_stage_from_finish(self.finish)
        for activity in self.inward_dict:
            if activity in finishers:
                self.slack_dict[activity]["lf"] = self.slack_dict[self.finish]["ls"]
                self.slack_dict[activity]["ls"] = self.slack_dict[activity]["lf"] - self.slack_dict[activity]["duration"]
        while len(finishers) > 0:
            i = 0
            new_finish = Activity
            temp_list = []
            for activity in finishers:
                new_finish = finishers[i]
                new_finishers = self.get_next_stage_from_finish(new_finish)
                for a in new_finishers:
                    if a not in temp_list:
                        temp_list.append(a)
                for node in self.inward_dict:
                    if node in new_finishers:
                        if self.slack_dict[node]["lf"] == 0 or self.slack_dict[node]["lf"] > self.slack_dict[new_finish]["ls"]:
                            self.slack_dict[node]["lf"] = self.slack_dict[new_finish]["ls"]
                            self.slack_dict[node]["ls"] = self.slack_dict[node]["lf"] - self.slack_dict[node]["duration"]
                i += 1
            finishers = temp_list
        for activity in self.slack_dict:
            self.slack_dict[activity]["slack"] = self.slack_dict[activity]["lf"]-self.slack_dict[activity]["ef"]
        logging.info("slack values has been calculated for graph: " + repr(self))

    ''''
    Question #4 - method that return slack value for each activity in descending order.
    '''
    def get_slack_time_descending(self):
        diction = {}
        for activity in self.slack_dict:
            if self.slack_dict[activity]["slack"] != 0:
                diction[activity] = self.slack_dict[activity]["slack"]
        logging.info("all activities with slack value !=0 and are connected to the graph: " + repr(self))
        return sorted(diction.items(), key=lambda x: x[1], reverse=True)

    '''
    Question #5 - return sum of all slacks in the project.
    '''
    def sum_of_slacks(self):
        sum_of_slacks = 0
        for activity in self.slack_dict:
            sum_of_slacks += self.slack_dict[activity]["slack"]
        logging.info("sum of all slacks in project has been calculated for graph: " + repr(self))
        return sum_of_slacks

    '''
    Finding all the paths available in the graph.
    '''
    def find_all_paths(self, start_activity, end_activity, path=[]):
        graph = self.outward_dict
        path = path + [start_activity]
        if start_activity == end_activity:
            return [path]
        if start_activity not in graph:
            return []
        paths = []
        for current_node in self.outward_dict[start_activity]:
            if current_node not in path or current_node == end_activity:
                extended_paths = self.find_all_paths(current_node, end_activity, path)
                if extended_paths:
                    paths += extended_paths
        logging.info("Returns all paths of the graph: " + repr(self) + " \npaths:" + str(paths))
        return paths

    '''
    Question #8 - Find critical path.
    checking all paths available in the graph for the path that all his activity's slack values are equal to zero.
    '''
    def find_critical_path(self):
        if len(self.outward_dict) > 0:
            counter = 0
            critical = {}
            all_paths = self.find_all_paths(self.start, self.finish)
            for path in all_paths:
                for activity in path:
                    if self.slack_dict[activity]["slack"] == 0:
                        counter += 1
                if counter == len(path):
                    critical = {node: node.duration for node in path}
                counter = 0
            logging.info("looking for critical path for graph: " + repr(self))
            return critical
        else: return None

    '''
    Question #9 - shorter duration on each activity in the critical path without leaving the critical path.
    '''
    def shorter_duration_dictionary(self):
        crit_path = self.find_critical_path()
        reformed_crit_path = {}
        maximum_shortage_diction = {activity: 0 for activity in crit_path}
        for activity in self.slack_dict:
            if activity in crit_path:
                counter = 0
                while self.slack_dict[activity]["duration"] > 1:
                    self.slack_dict[activity]["duration"] -= 1
                    self.calc_slack_vars(1)
                    reformed_crit_path = self.find_critical_path()
                    if reformed_crit_path != crit_path:
                        break
                    if reformed_crit_path == crit_path:
                        counter += 1
                self.slack_dict[activity]["duration"] = activity.duration
                maximum_shortage_diction[activity] = counter
        logging.info("looking for shorter duration for nodes within critical path.\nresult: " + str(maximum_shortage_diction))
        return maximum_shortage_diction


if __name__ == "__main__":
    start = Activity("start", 3)
    a = Activity("a", 2)
    b = Activity("b", 3)
    c = Activity("c", 6)
    d = Activity("d", 5)
    e = Activity("e", 4)
    f = Activity("f", 2)
    z = Activity("z", 4)
    finish = Activity("finish", 3)
    graph = {start: [a, b, c], a: [f], b: [d], c: [finish], d: [f, e], e: [finish], f: [finish], z: [], finish: []}

    '''Q1 - initialize graph'''
    print("GRAPH INITIALIZATION:")
    pert = Graph(graph)
    print(pert)
    print("\n")

    '''Q2 - add activity'''
    g = Activity("g", 2)
    h = Activity("h", 10)
    print("ADD ACTIVITIES:")
    pert.add_activity(g, [e], [finish])
    pert.add_activity(h) # 1 parameter (activity) means no connections (isolated)
    print(pert)
    print("\n")

    '''Q3 - isolated activities'''
    print("ISOLATED ACTIVITIES:")
    print(pert.isolated_activities())
    print("\n")

    '''Q4 - slack's time for each activity in descending order not including critical activities'''
    print("DESCENDING NONE SLACKS LIST:")
    print(pert.get_slack_time_descending())
    print("\n")

    '''Q5 - sum of slack time in project'''
    print("SUM OF SLACKS:")
    print(pert.sum_of_slacks())
    print("\n")

    '''
    Q6 - overwriting __str__ method for Graph class and Activity class.
    each written in own class body. Graph on line #48, Activity on line #15.
    '''

    '''
    Q7 - define iterator and iterate over all nodes inside "pert"
    iterator define on line #65.
    '''
    print("ITERATE OVER NODES IN 'PERT':")
    for node in pert.outward_dict:
        print(node)
    print("\n")

    '''Q8 - find "critical path" of the project'''
    print("CRITICAL PATH:")
    print(pert.find_critical_path())
    print("\n")

    '''
    Q9 - return dictionary containing each task in the "critical path" as key,
        and a value that represent maximum shorting time duration for the task without leaving the "critical path"
    '''
    print("MAXIMUM SHORTER DURATION DICTIONARY:")
    print(pert.shorter_duration_dictionary())
    print("\n")



