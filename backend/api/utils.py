def approve_user(user, admin_user):
    if not admin_user.is_authenticated or admin_user.role != 'admin':
        raise PermissionError("Seul un administrateur peut approuver les utilisateurs.")
    if user.is_approved:
        raise ValueError("L'utilisateur est déjà approuvé.")
    user.is_approved = True
    user.is_active = True
    user.save()