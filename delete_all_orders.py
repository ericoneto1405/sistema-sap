from meu_app import create_app, db
from meu_app.models import Pedido, ItemPedido, Pagamento, Coleta, ItemColetado
from config import DevelopmentConfig

def delete_all_orders():
    """
    Deletes all orders and related data from the database.
    This includes records from Pedido, ItemPedido, Pagamento, Coleta, and ItemColetado.
    """
    app = create_app(DevelopmentConfig)
    with app.app_context():
        try:
            print("Starting deletion...")
            # Deletion in the correct order to respect foreign key constraints
            num_item_coletado = db.session.query(ItemColetado).delete()
            print(f"{num_item_coletado} records deleted from ItemColetado")
            
            num_coleta = db.session.query(Coleta).delete()
            print(f"{num_coleta} records deleted from Coleta")
            
            num_pagamento = db.session.query(Pagamento).delete()
            print(f"{num_pagamento} records deleted from Pagamento")
            
            num_item_pedido = db.session.query(ItemPedido).delete()
            print(f"{num_item_pedido} records deleted from ItemPedido")
            
            num_pedido = db.session.query(Pedido).delete()
            print(f"{num_pedido} records deleted from Pedido")

            db.session.commit()

            print("\nDeletion successful!")
            print(f"  - Total {num_item_coletado} records deleted from ItemColetado")
            print(f"  - Total {num_coleta} records deleted from Coleta")
            print(f"  - Total {num_pagamento} records deleted from Pagamento")
            print(f"  - Total {num_item_pedido} records deleted from ItemPedido")
            print(f"  - Total {num_pedido} records deleted from Pedido")

        except Exception as e:
            db.session.rollback()
            print(f"An error occurred: {e}")
            print("Transaction rolled back.")

if __name__ == "__main__":
    print("This script will delete all orders and related data from the database.")
    print("This includes data from pedidos, financeiro, and coletas modules.")
    print("This action is irreversible.")
    confirm = input("Are you sure you want to continue? (yes/no): ")
    if confirm.lower() == 'yes':
        delete_all_orders()
    else:
        print("Operation cancelled.")