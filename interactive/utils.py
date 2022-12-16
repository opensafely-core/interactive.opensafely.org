def set_from_qs(qs, field="pk"):
    return set(qs.values_list(field, flat=True))
