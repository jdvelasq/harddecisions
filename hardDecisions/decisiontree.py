"""
Functions in this Module
==============================================================================


"""
from hardDecisions.treenode import *

class DecisionTree:
    """Creates and evaluates a decision tree model. """

    def __init__(self):
        """Decision tree constructor.
        """
        self.variables = []
        self.tree = []
        self.globals = {}
        self.cumvalue = 0

    def terminal_node(self, name=None, expr=None):
        """Creates a decision tree's terminal node.
        """
        self.variables.append({'tag':name,
                               'type':'TERMINAL',
                               'expr':expr})

    def chance_node(self, name=None, values=None, ignore=False):
        """Creates a decisions tree's internal chance node.
        """
        self.variables.append({'tag':name,
                               'type':'CHANCE',
                               'values':values,
                               'ignore':ignore})

    def decision_node(self, name=None, values=None, max=True, ignore=False):
        """Creates a decisions tree's internal decision node.
        """
        self.variables.append({'tag':name,
                               'type':'DECISION',
                               'values':values,
                               'max':max,
                               'ignore':ignore})

    def display_variables(self):
        """Display all the varibles in the decision tree.
        """
        txt = []
        for index, var in enumerate(self.variables):
            #
            txt.append('Node {:d}'.format(index))
            txt.append('    Name: ' + var.get('tag'))
            txt.append('    Type: ' + var.get('type'))
            #
            if  var.get('type') == 'DECISION':
                #
                if  var.get('max') is True:
                    txt[-1] += ' - Maximum Payoff'
                else:
                    txt[-1] += ' - Minimum Payoff'
                txt.append('    Branches:')
                txt.append('                      Outcomes  Sucessor Var')
                for (value, next_node) in var.get('values'):
                    txt.append('                  {:12.3f}  {:d}'.format(value, next_node))
                txt.append('')
                #
            elif  var.get('type') == 'CHANCE':
                #
                txt.append('    Branches:')
                txt.append('          Chance       Outcome  Sucessor Var')
                for (prob, value, next_node) in var.get('values'):
                    txt.append('           {:5.2f}  {:12.3f}  {:d}'.format(prob, value, next_node))
                txt.append('')
                #
            elif  var.get('type') == 'TERMINAL':
                #
                if var.get('expr') is None:
                    txt.append('    Expr: (cumulative)')
                else:
                    txt.append('    Expr: ' + var.get('expr'))
                txt.append('')
                #
            else:
                raise ValueError('Node type unknown: ' + var.tag + ', ' +  var.get('type'))
        print('\n'.join(txt))


    def build_tree(self):
        """Builds the decision tree using the information in the variables.
        """

        def build_node(current_node, var, var_list):

            if var.get('type') == 'TERMINAL':
                current_node['type'] = var['type']
                current_node['node_number'] = self.node_number
                current_node['expr'] = var['expr']
                current_node['expval'] = None
                current_node['terminal'] = var['tag']
                current_node['sel_strategy'] = None
                #
                if 'var' in current_node.keys() and current_node['ignore'] is False:
                    var_list.append(current_node['var'])
                #
                if var['expr'] is None:
                    expr = ''
                    for index, v in enumerate(var_list):
                        if index == 0:
                            expr = v
                        else:
                            expr += '+' + v
                    current_node['expr'] = expr
                self.node_number += 1

            if var.get('type') == 'CHANCE':
                #
                current_node['type'] = var['type']
                current_node['node_number'] = self.node_number
                current_node['expval']  = None
                current_node['sel_strategy'] = None
                current_node['forced_branch'] = None
                #
                if 'var' in current_node.keys() and current_node['ignore'] is False:
                    var_list.append(current_node['var'])
                #
                self.node_number += 1
                for child in var.get('values'):
                    prob, value, next_node = child
                    self.tree.append({'tag':len(self.tree)})
                    tree_node = self.tree[-1]
                    tree_node['var'] = var['tag']
                    tree_node['value'] = value
                    tree_node['prob'] = prob
                    #
                    tree_node['ignore'] = var['ignore']
                    #
                    if 'next_node' in current_node.keys():
                        current_node['next_node'].append(len(self.tree)- 1)
                    else:
                        current_node['next_node'] = [len(self.tree) - 1]
                    build_node(current_node=tree_node, var=self.variables[next_node], var_list=var_list.copy())

            if var.get('type') == 'DECISION':
                #
                current_node['type'] = var.get('type')
                current_node['max'] = var.get('max')
                current_node['node_number'] = self.node_number
                current_node['expval'] = None
                current_node['forced_branch'] = None
                current_node['sel_strategy'] = None
                #
                if 'var' in current_node.keys() and current_node['ignore'] is False:
                    var_list.append(current_node['var'])
                #
                self.node_number += 1
                for child in var.get('values'):
                    value, next_node = child
                    self.tree.append({'tag':len(self.tree)})
                    tree_node = self.tree[-1]
                    tree_node['var'] = var['tag']
                    tree_node['value'] = value
                    tree_node['expval'] = None
                    #
                    tree_node['ignore'] = var['ignore']
                    #
                    if 'next_node' in current_node.keys():
                        current_node['next_node'].append(len(self.tree) - 1)
                    else:
                        current_node['next_node'] = [len(self.tree) - 1]
                    build_node(current_node=tree_node, var=self.variables[next_node], var_list=var_list.copy())

        self.tree = []
        self.node_number = 0
        self.tree.append({'tag':0})
        var_list = []
        build_node(current_node=self.tree[0], var=self.variables[0], var_list=var_list.copy())


    def display_tree(self, maxdeep=None, selected_strategy=False):
        """Prints the tree as text.
        """

        def print_node(prefix, node, last_node):

            print(prefix + '|')

            type = node['type']
            if 'node_number' in node.keys():
                node_number = node['node_number']
                print(prefix + '| #' + str(node_number))


            ## prints the name and value of the variable
            if 'var' in node.keys():
                var = node['var']
                if 'value' in node.keys():
                    txt = "| " + var + "=" + str(node['value'])
                else:
                    txt = "| " + var
                print(prefix + txt)

            ## prints the probability
            if 'prob' in node.keys():
                txt = "| Prob={:1.2f}".format(node['prob'])
                print(prefix + txt)

            ## prints the cumulative probability
            if type == 'TERMINAL' and 'pathprob' in node.keys():
                txt = "| PathProb={:1.2f}".format(node['pathprob'])
                print(prefix + txt)

            if 'expval' in node.keys() and node['expval'] is not None:
                txt = "| ExpVal={:1.2f}".format(node['expval'])
                print(prefix + txt)

            if 'risk_profile' in node.keys() and type != 'TERMINAL':
                print(prefix + "| Risk Profile:")
                print(prefix + "|      Value  Prob")
                for key in sorted(node['risk_profile']):
                    txt = "|   {:8.2f} {:5.2f}".format(key, node['risk_profile'][key])
                    print(prefix + txt)

            if 'sel_strategy' in node.keys() and node['sel_strategy'] is True:
                txt = "| (selected strategy)"
                print(prefix + txt)

            if 'forced_branch' in node.keys() and node['forced_branch'] is not None:
                txt = "| (forced branch = {:1d})".format(node['forced_branch'])
                print(prefix + txt)


            next_node = node['next_node'] if 'next_node' in node.keys() else None

            if last_node:
                if type == 'DECISION':
                    txt = '\-------[D]'
                if type == 'CHANCE':
                    txt = '\-------[C]'
                if type == 'TERMINAL':
                    txt = '\-------[T] {:s}={:s}'.format(node['terminal'], node['expr'])
            else:
                if type == 'DECISION':
                    txt = '+-------[D]'
                if type == 'CHANCE':
                    txt = '+-------[C]'
                if type == 'TERMINAL':
                    txt = '+-------[T] {:s}={:s}'.format(node['terminal'], node['expr'])
            print(prefix + txt)

            if maxdeep is not None and self.current_deep == maxdeep:
                return

            self.current_deep += 1

            if next_node is not None:

                if selected_strategy is True and type == 'DECISION':
                    optbranch = node['opt_branch']
                    if last_node is True:
                        print_node(prefix + ' ' * 9, self.tree[next_node[optbranch]], last_node=True)
                    else:
                        print_node(prefix + '|' + ' ' * 8, self.tree[next_node[optbranch]], last_node=True)
                else:
                    for index, node in enumerate(next_node):
                        is_last_node = True if index == len(next_node) - 1 else False
                        if last_node is True:
                            print_node(prefix + ' ' * 9, self.tree[node], last_node=is_last_node)
                        else:
                            print_node(prefix + '|' + ' ' * 8, self.tree[node], last_node=is_last_node)

            self.current_deep -= 1

        self.current_deep = 0
        print_node(prefix='', node=self.tree[0], last_node=True)


    def evaluate(self):
        """Evalute the tree. First, the cumulative probabilities in all nodes
        are calculated. Finally, the algorithm computes the expected values."""

        def compute_values():
            """computes expected values.
            """
            def compute_node_value(node):

                type = node['type']

                if type == 'DECISION':
                    if 'var' in node.keys():
                        var = node['var']
                        value = node['value']
                        self.globals[var] = value
                    next_node = node['next_node']
                    ismax = node['max']
                    expval = None

                    for index, numnode in enumerate(next_node):
                        compute_node_value(node=self.tree[numnode])
                        if node['forced_branch'] is None:
                            if expval is None:
                                expval = self.tree[numnode].get('expval')
                                node['opt_branch'] = index
                            if ismax is True and expval < self.tree[numnode].get('expval'):
                                expval = self.tree[numnode].get('expval')
                                node['opt_branch'] = index
                            if ismax is False and expval > self.tree[numnode].get('expval'):
                                expval = self.tree[numnode].get('expval')
                                node['opt_branch'] = index
                        else:
                            if index == node['forced_branch']:
                                expval = self.tree[numnode].get('expval')
                                node['opt_branch'] = index

                    node['expval'] = expval


                if type == 'CHANCE':
                    var = node['var']
                    value = node['value']
                    self.globals[var] = value
                    next_node = node['next_node']
                    expval = 0
                    if node['forced_branch'] is None:
                        for numnode in next_node:
                            compute_node_value(node=self.tree[numnode])
                            expval += self.tree[numnode].get('expval') * self.tree[numnode].get('prob') / 100
                    else:
                        for index, numnode in enumerate(next_node):
                            if index == node['forced_branch']:
                                compute_node_value(node=self.tree[numnode])
                                expval += self.tree[numnode].get('expval')
                            else:
                                compute_node_value(node=self.tree[numnode])
                                expval += 0
                    node['expval'] = expval

                if type == 'TERMINAL':
                    var = node['var']
                    value = node['value']
                    self.globals[var] = value
                    node['expval'] = eval(node['expr'], self.globals.copy())

            compute_node_value(node=self.tree[0])


        def compute_prob():
            """Computes the probabilities in all tree branches.
            """
            def compute_node_prob(node, probability, sel_strategy):

                if node['type'] == 'DECISION':
                    node['sel_strategy'] = sel_strategy
                    if sel_strategy is True:
                        for index, numnode in enumerate(node['next_node']):
                            if index == node['opt_branch']:
                                compute_node_prob(node=self.tree[numnode],
                                                  probability=probability,
                                                  sel_strategy=True)
                            else:
                                compute_node_prob(node=self.tree[numnode],
                                                  probability=0,
                                                  sel_strategy=False)
                    else:
                        if sel_strategy is True:
                            current_prob = probability
                        else:
                            current_prob = 0
                        for numnode in node['next_node']:
                            compute_node_prob(node=self.tree[numnode],
                                              probability=current_prob,
                                              sel_strategy=False)
                if node['type'] == 'CHANCE':
                    node['sel_strategy'] = sel_strategy
                    if node['forced_branch'] is None:
                        for numnode in node['next_node']:
                            prob = self.tree[numnode]['prob']
                            compute_node_prob(node=self.tree[numnode],
                                              probability=probability * prob/100,
                                              sel_strategy = sel_strategy)
                    else:
                        for index, numnode in enumerate(node['next_node']):
                            if index == node['forced_branch']:
                                prob = self.tree[numnode]['prob']
                                prob = 100
                                compute_node_prob(node=self.tree[numnode],
                                                  probability=probability * prob/100,
                                                  sel_strategy = True)
                            else:
                                prob = self.tree[numnode]['prob']
                                prob = 0
                                compute_node_prob(node=self.tree[numnode],
                                                  probability=probability * prob/100,
                                                  sel_strategy = False)
                if node['type'] == 'TERMINAL':
                    node['sel_strategy'] = sel_strategy
                    node['pathprob'] = probability * 100
            #
            compute_node_prob(node=self.tree[0], probability=1.0, sel_strategy=True)

        self.cumvalue = 0
        compute_values()
        compute_prob()



    def compute_risk_profile(self):
        """Computes the risk profile for the selected strategy.
        """

        def collect(node):

            if node['sel_strategy'] is False:
                return

            if node['type'] == 'DECISION':
                for index, numnode in enumerate(node['next_node']):
                    collect(node=self.tree[numnode])
                next_opt_branch = node['next_node'][node['opt_branch']]
                node['risk_profile'] = self.tree[next_opt_branch]['risk_profile']

            if node['type'] == 'CHANCE':
                for index, numnode in enumerate(node['next_node']):
                    collect(node=self.tree[numnode])
                node['risk_profile'] = {}
                for numnode in node['next_node']:
                    dict = self.tree[numnode]['risk_profile']
                    for key in dict.keys():
                        if key in node['risk_profile'].keys():
                            node['risk_profile'][key] += dict[key]
                        else:
                            node['risk_profile'][key] = dict[key]


            if node['type'] == 'TERMINAL':
                node['risk_profile'] = {node['expval']: node['pathprob']}


        collect(node=self.tree[0])




if __name__ == "__main__":
    import doctest
    doctest.testmod()
