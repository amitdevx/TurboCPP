
/* WARNING: C89 compliance issues detected:
 * Line 111: Declaration after statements in block block (C89 violation) - 'struct node *newNode;'
 * Line 210: Declaration after statements in block block (C89 violation) - 'struct node *temp;'
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

struct node *createNode(int value);
struct node *insertNode(struct node *root, int value);
void inorderTraversal(struct node *root);
void preorderTraversal(struct node *root);
void postorderTraversal(struct node *root);
struct node *searchNode(struct node *root, int value);
struct node *findMin(struct node *root);
struct node *findMax(struct node *root);
struct node *deleteNode(struct node *root, int value);

void main()
{
    int choice, value;
    struct node *root = NULL;
    struct node *result;
    
    clrscr();
    
    while(1) {
        printf("\n--- BINARY SEARCH TREE MENU ---\n");
        printf("1. Insert a node\n");
        printf("2. Inorder traversal\n");
        printf("3. Preorder traversal\n");
        printf("4. Postorder traversal\n");
        printf("5. Search for a node\n");
        printf("6. Find minimum value\n");
        printf("7. Find maximum value\n");
        printf("8. Delete a node\n");
        printf("9. Exit\n");
        printf("Enter your choice: ");
        scanf("%d", &choice);
        
        switch(choice) {
            case 1:
                printf("Enter value to insert: ");
                scanf("%d", &value);
                root = insertNode(root, value);
                printf("Node inserted successfully.\n");
                break;
                
            case 2:
                printf("Inorder traversal: ");
                inorderTraversal(root);
                printf("\n");
                break;
                
            case 3:
                printf("Preorder traversal: ");
                preorderTraversal(root);
                printf("\n");
                break;
                
            case 4:
                printf("Postorder traversal: ");
                postorderTraversal(root);
                printf("\n");
                break;
                
            case 5:
                printf("Enter value to search: ");
                scanf("%d", &value);
                result = searchNode(root, value);
                if(result != NULL) {
                    printf("Value %d found in the tree.\n", value);
                } else {
                    printf("Value %d not found.\n", value);
                }
                break;
                
            case 6:
                result = findMin(root);
                if(result != NULL) {
                    printf("Minimum value: %d\n", result->data);
                } else {
                    printf("Tree is empty.\n");
                }
                break;
                
            case 7:
                result = findMax(root);
                if(result != NULL) {
                    printf("Maximum value: %d\n", result->data);
                } else {
                    printf("Tree is empty.\n");
                }
                break;
                
            case 8:
                printf("Enter value to delete: ");
                scanf("%d", &value);
                root = deleteNode(root, value);
                printf("Deletion operation completed.\n");
                break;
                
            case 9:
                printf("Exiting program.\n");
                getch();
                exit(0);
                
            default:
    struct node *newNode;
                printf("Invalid choice! Please try again.\n");
        }
        getch();
    }
}

struct node *createNode(int value)
{
    newNode = (struct node *)malloc(sizeof(struct node));
    newNode->data = value;
    newNode->left = NULL;
    newNode->right = NULL;
    return newNode;
}

struct node *insertNode(struct node *root, int value)
{
    if(root == NULL) {
        return createNode(value);
    }
    
    if(value < root->data) {
        root->left = insertNode(root->left, value);
    } else if(value > root->data) {
        root->right = insertNode(root->right, value);
    }
    
    return root;
}

void inorderTraversal(struct node *root)
{
    if(root != NULL) {
        inorderTraversal(root->left);
        printf("%d ", root->data);
        inorderTraversal(root->right);
    }
}

void preorderTraversal(struct node *root)
{
    if(root != NULL) {
        printf("%d ", root->data);
        preorderTraversal(root->left);
        preorderTraversal(root->right);
    }
}

void postorderTraversal(struct node *root)
{
    if(root != NULL) {
        postorderTraversal(root->left);
        postorderTraversal(root->right);
        printf("%d ", root->data);
    }
}

struct node *searchNode(struct node *root, int value)
{
    if(root == NULL || root->data == value) {
        return root;
    }
    
    if(value < root->data) {
        return searchNode(root->left, value);
    } else {
        return searchNode(root->right, value);
    }
}

struct node *findMin(struct node *root)
{
    if(root == NULL) {
        return NULL;
    }
    
    while(root->left != NULL) {
        root = root->left;
    }
    
    return root;
}

struct node *findMax(struct node *root)
{
    if(root == NULL) {
        return NULL;
    }
    
    while(root->right != NULL) {
        root = root->right;
    }
    
    return root;
}

struct node *deleteNode(struct node *root, int value)
{
    struct node *temp;
    
    if(root == NULL) {
        return root;
    }
    
    if(value < root->data) {
        root->left = deleteNode(root->left, value);
    } else if(value > root->data) {
        root->right = deleteNode(root->right, value);
    } else {
        if(root->left == NULL) {
            temp = root->right;
            free(root);
            return temp;
        } else if(root->right == NULL) {
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
