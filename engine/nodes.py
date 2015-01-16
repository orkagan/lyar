import html

class Node:

    def __init__(self):
        pass

    def render(self, context):
        raise NotImplementedError()

class TextNode(Node):

    def __init__(self, content):
        self.content = content

    def render(self, context):
        return self.content

    def __str__(self):
        return "TextNode: " + self.content

    def __repr__(self):
        return "TextNode"

class PythonNode(Node):

    def __init__(self, code):
        self.code = code

    def render(self, context):
        try:
            output = eval(self.code, {}, context)
        except NameError:
            raise NameError("Required variable not defined in context.")
        else:
            return html.escape(str(output))

    def __str__(self):
        return "PythonNode: " + self.code

    def __repr__(self):
        return "PythonNode"

class SafeNode(PythonNode):
    def render(self, context):
        try:
            output = eval(self.code, {}, context)
        except NameError:
            raise NameError("Required variable in safe statement not defined in context.")
        else:
            return str(output)

    def __str__(self):
        return "SafeNode: " + self.code

    def __repr__(self):
        return "SafeNode"

class GroupNode(Node):

    def __init__(self, children=None):
        if children is not None:
            self.children = children
        else:
            self.children = []

    def render(self, context):
        finalStr = ""
        for child in self.children:
            finalStr += child.render(context)
        return finalStr

    def addChild(self, node):
        self.children.append(node)

    def __repr__(self):
        return "GroupNode"

    def __str__(self):
        return "GroupNode: " + str(self.children)

class IfNode(Node):

    def __init__(self, predicate):
        self.predicate = predicate
        self.trueNode = GroupNode()
        self.falseNode = GroupNode()

    def addTrueChild(self, node):
        self.trueNode.addChild(node)

    def addFalseChild(self, node):
        self.falseNode.addChild(node)

    def render(self, context):
        try:
            result = eval(self.predicate, {}, context)
        except NameError:
            raise NameError("Required variable in if predicate not defined in context. Context is {}".format(context))
        else:
            if result:
                return self.trueNode.render(context)
            else:
                return self.falseNode.render(context)

    def __repr__(self):
        left = '...' if self is self.trueNode else str(self.trueNode)
        right = '...' if self is self.falseNode else str(self.falseNode)
        return 'IfNode({}, {}, {})'.format(id(self), left, right)


class ForNode(Node):
    def __init__(self, iterable, variable):
        self.loopBlock = GroupNode()
        self.iterable = iterable
        self.variable = variable

    def addLoopChild(self, node):
        self.loopBlock.addChild(node)

    def render(self, context):
        try:
            iterating = eval(self.iterable, {}, context)
        except NameError:
            raise NameError("Required variable in for loop iterable not defined in context.")
        else:
            out = ""
            for item in iterating:
                newContext = dict(context) # new instance
                newContext[self.variable] = item
                out += self.loopBlock.render(newContext)
            return out

class CommentNode(Node):
    def __init__(self, comment):
        self.comment = comment

    def render(self, context):
        return ''
