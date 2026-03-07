/* @ai implement a binary tree with operations create,seach,insert,inorder,preorder,postorder. write menu driven pogram to perform above operations */
/* @ai-generated-start */
#include <stdio.h>
#include <conio.h>
#include <stdlib.h>

typedef struct TreeNode {
    int data;
    struct TreeNode *left;
    struct TreeNode *right;
} TreeNode;

TreeNode *root = NULL;

/* Function to create a new node */
TreeNode *createNode(int data) {
    TreeNode *newNode = (TreeNode *)malloc(sizeof(TreeNode));
    if (newNode == NULL) {
        printf("Memory allocation failed!\n");
        exit(1);
    }
    newNode->data = data;
    newNode->left = NULL;
    newNode->right = NULL;
    return newNode;
}

/* Function to insert a node into the binary tree */
void insertNode(int data) {
    TreeNode *newNode = createNode(data);
    TreeNode *current;
    TreeNode *parent;

    if (root == NULL) {
        root = newNode;
        return;
    }
    current = root;
    parent = NULL;
    while (current != NULL) {
        parent = current;
        if (data < current->data) {
            current = current->left;
        } else if (data > current->data) {
            current = current->right;
        } else {
            printf("Duplicate value not allowed.\n");
            free(newNode);
            return;
        }
    }
    if (data < parent->data) {
        parent->left = newNode;
    } else {
        parent->right = newNode;
    }
}

/* Function to search for a node in the binary tree */
TreeNode *searchNode(int data) {
    TreeNode *current = root;
    while (current != NULL) {
        if (data == current->data) {
            return current;
        } else if (data < current->data) {
            current = current->left;
        } else {
            current = current->right;
        }
    }
    return NULL;
}

/* Inorder traversal */
void inorder(TreeNode *root) {
    if (root != NULL) {
        inorder(root->left);
        printf("%d ", root->data);
        inorder(root->right);
    }
}

/* Preorder traversal */
void preorder(TreeNode *root) {
    if (root != NULL) {
        printf("%d ", root->data);
        preorder(root->left);
        preorder(root->right);
    }
}

/* Postorder traversal */
void postorder(TreeNode *root) {
    if (root != NULL) {
        postorder(root->left);
        postorder(root->right);
        printf("%d ", root->data);
    }
}

void main() {
                TreeNode *foundNode;

    int choice, data;
    clrscr();
    while (1) {
        printf("\nBinary Tree Menu:\n");
        printf("1. Insert Node\n");
        printf("2. Search Node\n");
        printf("3. Inorder Traversal\n");
        printf("4. Preorder Traversal\n");
        printf("5. Postorder Traversal\n");
        printf("6. Exit\n");
        printf("Enter your choice: ");
        scanf("%d", &choice);
        switch (choice) {
            case 1:
                printf("Enter data to insert: ");
                scanf("%d", &data);
                insertNode(data);
                break;
            case 2:
                printf("Enter data to search: ");
                scanf("%d", &data);
                foundNode = searchNode(data);
                if (foundNode != NULL) {
                    printf("Node found with data: %d\n", foundNode->data);
                } else {
                    printf("Node not found.\n");
                }
                break;
            case 3:
                printf("Inorder Traversal: ");
                inorder(root);
                printf("\n");
                break;
            case 4:
                printf("Preorder Traversal: ");
                preorder(root);
                printf("\n");
                break;
            case 5:
                printf("Postorder Traversal: ");
                postorder(root);
                printf("\n");
                break;
            case 6:
                exit(0);
            default:
                printf("Invalid choice. Please try again.\n");
        }
    }
    getch();
}
/* @ai-generated-end */
