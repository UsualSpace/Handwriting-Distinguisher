import os
import torch
import torch.nn as nn
import torch.optim as optim
import torch.utils.data as data
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, accuracy_score
from collections import Counter

path_to_main_directory = os.path.dirname(os.getcwd())
path = f"{path_to_main_directory}/dataset/training_data"

target_size = (78, 555)
batch_size = 32
num_epochs = 20
learning_rate = 0.0005

data_list = []
labels_list = []
class_to_idx = {}

# Convert images into tensors
def preprocess_image(image_path):
    # img = Image.open(image_path).resize(target_size)
    img = Image.open(image_path)
    img_array = np.array(img)
    # img_tensor = torch.tensor(img_array).permute(2, 0, 1)
    img_tensor = torch.tensor(img_array)
    img_tensor = img_tensor.float() / 255.0
    return img_tensor

# Load images
for idx, class_name in enumerate(os.listdir(path)):
    if class_name.startswith("."):
        pass
    else:
        class_to_idx[class_name]= idx
        class_dir = os.path.join(path, class_name)

        for filename in os.listdir(class_dir):
            if filename.endswith(('.jpg', '.png', '.jpeg')):
                img_path = os.path.join(class_dir, filename)
                data_list.append(preprocess_image(img_path))
                labels_list.append(idx - 1)

# Balance dataset
balanced_data, balanced_labels = [], []
min_samples = min([labels_list.count(c) for c in np.unique(labels_list)])

for class_label in np.unique(labels_list):
    class_indices = [i for i, label in enumerate(labels_list) if label == class_label]
    sampled_indices = np.random.choice(class_indices, min_samples, replace=False)

    for idx in sampled_indices:
        balanced_data.append(data_list[idx])
        balanced_labels.append(labels_list[idx])

# Convert to tensors
data_tensor = torch.stack(balanced_data)
labels_tensor = torch.tensor(balanced_labels, dtype=torch.long)
# print(balanced_labels, "\nclass indices",class_indices, "\nsampled indices",sampled_indices)

# Split into training and validation sets
X_train, X_val, y_train, y_val = train_test_split(
    data_tensor, labels_tensor, test_size=0.2, stratify=labels_tensor, random_state=42
)

# Create DataLoaders
train_dataset = data.TensorDataset(X_train, y_train)
train_loader = data.DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

val_dataset = data.TensorDataset(X_val, y_val)
val_loader = data.DataLoader(val_dataset, batch_size=batch_size, shuffle=True)

# Define Neural Network
class HandwritingNet(nn.Module):
    def __init__(self, num_classes):
        super(HandwritingNet, self).__init__()
        self.flatten = nn.Flatten()
        # self.fc1 = nn.Linear(224 * 224 * 3, 125)
        self.fc1 = nn.Linear(78 * 555, 125)
        self.bn1 = nn.BatchNorm1d(125)
        self.relu1 = nn.ReLU()
        self.dropout1 = nn.Dropout(0.3)

        self.fc2 = nn.Linear(125, 75)
        self.bn2 = nn.BatchNorm1d(75)
        self.relu2 = nn.ReLU()
        self.dropout2 = nn.Dropout(0.3)

        self.fc3 = nn.Linear(75, 25)
        self.bn3 = nn.BatchNorm1d(25)
        self.relu3 = nn.ReLU()

        self.fc4 = nn.Linear(25, num_classes)

    def forward(self, x):
        x = self.flatten(x)
        x = self.dropout1(self.relu1(self.bn1(self.fc1(x))))
        x = self.dropout2(self.relu2(self.bn2(self.fc2(x))))
        x = self.relu3(self.bn3(self.fc3(x)))
        x = self.fc4(x)
        return x

# Initialize model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
num_classes = len(class_to_idx)
model = HandwritingNet(num_classes).to(device)

# Compute class weights

y_train_numpy = y_train.numpy()
class_counts = Counter(y_train_numpy)
# print("Class counts:", class_counts)
# for i in range(len(class_counts)):
#     print(class_counts[i+1])
class_weights = torch.tensor([1.0 / class_counts[i] for i in range(len(class_counts))], dtype=torch.float32).to(device)

# Define loss function and optimizer
criterion = nn.CrossEntropyLoss(weight=class_weights)
optimizer = optim.Adam(model.parameters(), lr=learning_rate)
scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.5)  # Reduce LR every 5 epochs

# Train the Model
train_accuracies = []

for epoch in range(num_epochs):
    model.train()
    total_loss = 0
    correct = 0
    total = 0

    for inputs, targets in train_loader:
        inputs, targets = inputs.to(device), targets.to(device)

        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, targets)
        loss.backward()
        optimizer.step()

        total_loss += loss.item()
        _, predicted = torch.max(outputs, 1)
        correct += (predicted == targets).sum().item()
        total += targets.size(0)

    train_acc = 100 * correct / total
    train_accuracies.append(train_acc)
    print(f"Epoch [{epoch+1}/{num_epochs}], Loss: {total_loss:.4f}, Accuracy: {train_acc:.2f}%")
    scheduler.step()

# Save the model
model_path = "handwriting_classification_model.pth"
torch.save(model.state_dict(), model_path)
print(f"Model saved to {model_path}")

# Function to evaluate model and save confusion matrices
def evaluate_model(loader, dataset_type):
    model.eval()
    all_preds = []
    all_targets = []

    with torch.no_grad():
        for inputs, targets in loader:
            inputs, targets = inputs.to(device), targets.to(device)
            outputs = model(inputs)
            _, predicted = torch.max(outputs, 1)
            all_preds.extend(predicted.cpu().numpy())
            all_targets.extend(targets.cpu().numpy())

    # Compute Confusion Matrix
    cm = confusion_matrix(all_targets, all_preds)
    acc = accuracy_score(all_targets, all_preds)
    
    # Save Confusion Matrix Plot
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=class_to_idx.keys(), yticklabels=class_to_idx.keys())
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title(f"{dataset_type} Confusion Matrix (Accuracy: {acc:.2f})")
    
    cm_filename = f"{dataset_type.lower()}_confusion_matrix.png"
    plt.savefig(cm_filename)
    print(f"{dataset_type} confusion matrix saved as {cm_filename}")
    plt.close()

# Load model
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# num_classes = 7
# model = HandwritingNet(num_classes).to(device)

# Load saved weights
# model.load_state_dict(torch.load("sentence_classification_model.pth", map_location=device))
# model.eval()
# Evaluate on Training and Validation Data

evaluate_model(train_loader, "Train")
evaluate_model(val_loader, "Validation")

# Save Training Accuracy Plot
plt.figure(figsize=(8, 6))
plt.plot(range(1, num_epochs + 1), train_accuracies, marker='o', linestyle='-', color='b', label="Training Accuracy")
plt.xlabel("Epoch")
plt.ylabel("Accuracy (%)")
plt.title("Training Accuracy Across Epochs")
plt.legend()
plt.grid()
plt.savefig("training_accuracy.png")
print("Training accuracy chart saved as training_accuracy.png")
plt.close()
