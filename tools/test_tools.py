from telecom_tools import lookup_customer, get_service_status, create_ticket, retrieve_faq

print("=== TEST 1: Lookup Customer ===")
result = lookup_customer("0612345678")
print(result)

print("\n=== TEST 2: Service Status ===")
result = get_service_status()
print(result)

print("\n=== TEST 3: Create Ticket ===")
result = create_ticket("C001", "Problème de connexion 4G", "high")
print(result)

print("\n=== TEST 4: FAQ ===")
result = retrieve_faq("facture")
print(result)