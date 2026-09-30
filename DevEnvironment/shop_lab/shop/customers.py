def format_customer_info(name: str, email: str) -> str:
    normalized_name = name.strip()
    normalized_email = email.strip().lower()
    if not normalized_name:
        raise ValueError("Customer name is required")
    local_part, separator, domain = normalized_email.partition("@")
    if not separator or not local_part or "." not in domain:
        raise ValueError("Enter a valid customer email")
    return f"Customer: {normalized_name} ({normalized_email})"
