from app.core.security import hash_password

def update_user(db, user, data):
    updates = data.model_dump(exclude_unset=True)
    if "kata_sandi" in updates:
        updates["kata_sandi"] = hash_password(updates["kata_sandi"])
    for key, value in updates.items():
        setattr(user, key, value)
    db.commit()
    return user