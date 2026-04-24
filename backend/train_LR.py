import pandas as pd
import pickle
import numpy as np
import os
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt

# Paths based on user input
dataset_folder = r"C:\Users\asus\Desktop\final year project\processed dataset"
dataset_file = "cleaned_legal_dataset.csv"
vectorizer_file = "tfidf_vectorizer.pkl"
model_folder = r"C:\Users\asus\Desktop\final year project\model"

print("Loading dataset...")
# Load dataset
df = pd.read_csv(os.path.join(dataset_folder, dataset_file))

# Handle text column (in case of nulls)
df['preprocessed'] = df['preprocessed'].fillna('')

file_path = os.path.join(dataset_folder, vectorizer_file)

print("Loading vectorizer...")
with open(file_path, "rb") as f:
    vectorizer = pickle.load(f)

# Feature matrix and target
print("Transforming text...")
X = vectorizer.transform(df['preprocessed'])  # Use only transform as per friend's code
y = df['label']

# Setup 5-Fold Cross-Validation
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

fold = 1
accuracies = []
precision_scores = []
recall_scores = []
f1_scores = []
all_true = []
all_preds = []

print("Starting cross-validation...")
for train_index, test_index in skf.split(X, y):
    print(f"\n--- Fold {fold} ---")

    X_train, X_val = X[train_index], X[test_index]
    y_train, y_val = y.iloc[train_index], y.iloc[test_index]

    # Train model
    # Note: max_iter=1000 is used for LogisticRegression to ensure convergence, especially on text data
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)

    # Predict
    predictions = model.predict(X_val)

    # Evaluation
    acc = accuracy_score(y_val, predictions)
    report_dict = classification_report(y_val, predictions, output_dict=True, zero_division=0)

    # Macro average scores 
    precision_scores.append(report_dict["macro avg"]["precision"])
    recall_scores.append(report_dict["macro avg"]["recall"])
    f1_scores.append(report_dict["macro avg"]["f1-score"])
    accuracies.append(acc)

    print(f"Accuracy: {acc:.4f}")
    print("Classification Report:\n", classification_report(y_val, predictions, digits=4, zero_division=0))
    
    all_true.extend(y_val)
    all_preds.extend(predictions)
    fold += 1

# Final averaged metrics
print("\n==============================")
print(f"Average Accuracy: {np.mean(accuracies):.4f}")
print(f"Average Precision (macro avg): {np.mean(precision_scores):.4f}")
print(f"Average Recall (macro avg): {np.mean(recall_scores):.4f}")
print(f"Average F1-score (macro avg): {np.mean(f1_scores):.4f}")

# Save logistic_regression_model
print("\nSaving model...")
os.makedirs(model_folder, exist_ok=True)
model_save_path = os.path.join(model_folder, "logistic_regression_model.pkl")
with open(model_save_path, "wb") as f:
    pickle.dump(model, f)
print(f"Model successfully saved to: {model_save_path}")

# Overall confusion matrix
cm_total = confusion_matrix(all_true, all_preds)
print("\n=== Overall Confusion Matrix ===")
print(cm_total)

# Visualize Confusion Matrix
print("\nPlotting confusion matrix...")
disp = ConfusionMatrixDisplay(confusion_matrix=cm_total, display_labels=model.classes_)

# Adjust figure size based on number of classes (legal matters usually have several)
fig, ax = plt.subplots(figsize=(10, 10))   
disp.plot(cmap='Blues', ax=ax, values_format='d', xticks_rotation='vertical')   
plt.title("Overall Confusion Matrix (Logistic Regression)")
plt.tight_layout()

print("Saving plot to confusion_matrix_lr.png. Finished execution.")
plt.savefig("confusion_matrix_lr.png")
# plt.show()    
