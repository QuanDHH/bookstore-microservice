import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, SimpleRNN, Dense, Dropout, LSTM, Bidirectional

# Load data
df = pd.read_csv("data_user500.csv")
df = df.sort_values(["user_id", "timestamp"]).reset_index(drop=True)

le = LabelEncoder()
df["action_enc"] = le.fit_transform(df["action"])

SEQUENCE_LENGTH = 10
sequences, labels = [], []

for uid, group in df.groupby("user_id"):
    actions = group["action_enc"].tolist()
    for i in range(len(actions) - SEQUENCE_LENGTH):
        sequences.append(actions[i:i+SEQUENCE_LENGTH])
        labels.append(actions[i+SEQUENCE_LENGTH])

X = pad_sequences(sequences, maxlen=SEQUENCE_LENGTH, padding="pre")
y = np.array(labels)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Build BiLSTM model
def build_bilstm(vocab_size, seq_len, num_classes):
    model = Sequential([
        Embedding(vocab_size, 64, input_length=seq_len),
        Bidirectional(LSTM(128, return_sequences=True)),
        Bidirectional(LSTM(64, return_sequences=False)),
        Dropout(0.3),
        Dense(64, activation="relu"),
        Dropout(0.2),
        Dense(num_classes, activation="softmax")
    ])
    model.compile(optimizer="adam",
                  loss="sparse_categorical_crossentropy",
                  metrics=["accuracy"])
    return model

bilstm_model = build_bilstm(len(le.classes_), SEQUENCE_LENGTH, len(le.classes_))
bilstm_model.fit(X_train, y_train, epochs=30, batch_size=64, validation_split=0.15, verbose=1)

# Save model
bilstm_model.save("model_best.h5")
print("Model saved as model_best.h5")