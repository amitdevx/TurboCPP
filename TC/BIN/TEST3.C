
/* WARNING: C89 compliance issues detected:
 * Line 107: Declaration after statements in block block (C89 violation) - 'struct node *newNode;'
 * Line 170: Declaration after statements in block block (C89 violation) - 'struct node *temp;'
 * Fix: Move ALL variable declarations to top of blocks.
 */

#include <stdio.h>
#include <conio.h>
#include <stdlib.h>

struct node {
    int data;
    struct node *left;
    struct node *right;
};

struct node* createNode(int value);
struct node* insertNode(struct node* root, int value);
struct node* deleteNode(struct node* root, int value);
struct node* searchNode(struct node* root, int value);
void inorderTraversal(struct node* root);
void preorderTraversal(struct node* root);
void postorderTraversal(struct node* root);
int countNodes(struct node* root);
int findHeight(struct node* root);
struct node* findMin(struct node* root);

void main()
{
    struct node *root = NULL;
    int choice, value, result;
    struct node *found;
    
    clrscr();
    
    while(1)
    {
        printf("\n--- BINARY SEARCH TREE MENU ---\n");
        printf("1. Insert node\n");
        printf("2. Delete node\n");
        printf("3. Search node\n");
        printf("4. Inorder traversal\n");
        printf("5. Preorder traversal\n");
        printf("6. Postorder traversal\n");
        printf("7. Count total nodes\n");
        printf("8. Find height of tree\n");
        printf("9. Exit\n");
        printf("Enter your choice: ");
        scanf("%d", &choice);
        
        switch(choice)
        {
            case 1:
                printf("Enter value to insert: ");
                scanf("%d", &value);
                root = insertNode(root, value);
                printf("Node inserted successfully.\n");
                break;
                
            case 2:
                printf("Enter value to delete: ");
                scanf("%d", &value);
                root = deleteNode(root, value);
                printf("Deletion attempted.\n");
                break;
                
            case 3:
                printf("Enter value to search: ");
                scanf("%d", &value);
                found = searchNode(root, value);
                if(found != NULL)
                {
                    printf("Value %d found in the tree.\n", value);
                }
                else
                {
                    printf("Value %d not found.\n", value);
                }
                break;
                
            case 4:
                printf("Inorder traversal: ");
                inorderTraversal(root);
                printf("\n");
                break;
                
            case 5:
                printf("Preorder traversal: ");
                preorderTraversal(root);
                printf("\n");
                break;
                
            case 6:
                printf("Postorder traversal: ");
                postorderTraversal(root);
                printf("\n");
                break;
                
            case 7:
                result = countNodes(root);
                printf("Total nodes: %d\n", result);
                break;
                
            case 8:
                result = findHeight(root);
                printf("Height of tree: %d\n", result);
                break;
                
            case 9:
                exit(0);
                
            default:
    struct node *newNode;
                printf("Invalid choice! Please try again.\n");
        }
        getch();
    }
}

struct node* createNode(int value)
{
    newNode = (struct node*)malloc(sizeof(struct node));
    newNode->data = value;
    newNode->left = NULL;
    newNode->right = NULL;
    return newNode;
}

struct node* insertNode(struct node* root, int value)
{
    if(root == NULL)
    {
        return createNode(value);
    }
    
    if(value < root->data)
    {
        root->left = insertNode(root->left, value);
    }
    else if(value > root->data)
    {
        root->right = insertNode(root->right, value);
    }
    
    return root;
}

struct node* searchNode(struct node* root, int value)
{
    if(root == NULL || root->data == value)
    {
        return root;
    }
    
    if(value < root->data)
    {
        return searchNode(root->left, value);
    }
    else
    {
        return searchNode(root->right, value);
    }
}

struct node* findMin(struct node* root)
{
    while(root->left != NULL)
    {
        root = root->left;
    }
    return root;
}

struct node* deleteNode(struct node* root, int value)
{
    struct node *temp;
    
    if(root == NULL)
    {
        return root;
    }
    
    if(value < root->data)
    {
        root->left = deleteNode(root->left, value);
    }
    else if(value > root->data)
    {
        root->right = deleteNode(root->right, value);
    }
    else
    {
        if(root->left == NULL)
        {
            temp = root->right;
            free(root);
            return temp;
        }
        else if(root->right == NULL)
        {
            temp = root->left;
            free(root);
            return temp;
        }
        
        temp = findMin(root->right);
        root->data = temp->data;
        root->right = deleteNode(root->right, temp->data);
    }
    
    return root;
}

void inorderTraversal(struct node* root)
{
    if(root != NULL)
    {
        inorderTraversal(root->left);
        printf("%d ", root->data);
        inorderTraversal(root->right);
    }
}

void preorderTraversal(struct node* root)
{
    if(root != NULL)
    {
        printf("%d ", root->data);
        preorderTraversal(root->left);
        preorderTraversal(root->right);
    }
}

void postorderTraversal(struct node* root)
{
    if(root != NULL)
    {
        postorderTraversal(root->left);
        postorderTraversal(root->right);
        printf("%d ", root->data);
    }
}

int countNodes(struct node* root)
{
    if(root == NULL)
    {
        return 0;
    }
    return 1 + countNodes(root->left) + countNodes(root->right);
}

int findHeight(struct node* root)
{
    int leftHeight, rightHeight;
    
    if(root == NULL)
    {
        return 0;
    }
    
    leftHeight = findHeight(root->left);
    rightHeight = findHeight(root->right);
    
    if(leftHeight > rightHeight)
    {
        return leftHeight + 1;
    }
    else
    {
        return rightHeight + 1;
    }
}
