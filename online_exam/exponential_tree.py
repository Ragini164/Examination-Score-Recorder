#Start of PRoject

class ExponentialTree:
    
    class Nodee:#data in the tree
        def __init__(self, data_element):
            #Initilization of the tree elements
            self.data_element=data_element #holds data
            self.currentnodelevel=1 #current node level
            self.right=None #right node
            self.left=None #left node
            self.child=[] #child nodes
            self.NewNode=None
            self.child.insert(self.currentnodelevel,self.NewNode)

    def __init__(self): 
        self.root=None #root node

    def  insert(self,newValue):
        self.root = self.insertNode(self.root,self.Nodee(newValue)) #basic insert function
        
    def insertNode(self,root,newNode):
        if (root == None):
            root = self.Nodee(newNode.data_element)
            return root
        

        self.incrementNodes(root)
        #insert in sorted position
        if (newNode.data_element['score'] <= root.data_element['score']):
            root.left = self.insertNode(root.left, newNode)
        elif (newNode.data_element['score'] >= root.data_element['score']): 
            root.right = self.insertNode(root.right, newNode)
        return root

    def incrementNodes(self, root): #increment of nodes
        root.currentnodelevel = root.currentnodelevel * 2;
    # Depth first Search or Depth first traversal is a recursive algorithm for searching all the vertices of a graph or tree data structure. Traversal means visiting all the nodes of a
    def inorderTraversal(self,root): #inorder dfs traversal
        res = []
    #     // Mark the current node as visited and
    # // print it
        if root:
            # Call the recursive helper function
        # to print DFS traversal
            res = self.inorderTraversal(root.right)
            res.append(root.data_element)
            # Call the recursive helper function
        # to print DFS traversal
            res = res + self.inorderTraversal(root.left) 
        return res


