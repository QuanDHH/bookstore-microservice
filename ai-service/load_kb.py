from app.recommendation_engine import KBGraphBuilder

# Load data into KB Graph
kb = KBGraphBuilder()
kb.create_constraints()
kb.load_data("data_user500.csv")
kb.close()
print("KB Graph loaded successfully!")