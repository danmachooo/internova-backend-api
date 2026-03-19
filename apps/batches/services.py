class BatchService:
    @staticmethod
    def list_batch_interns(*, batch):
        from django.apps import apps

        if not apps.is_installed("apps.interns"):
            return []

        try:
            intern_profile_model = apps.get_model("interns", "InternProfile")
        except LookupError:
            return []

        profiles = (
            intern_profile_model.objects.select_related("user")
            .filter(batch=batch)
            .order_by("user__name")
        )
        return [
            {
                "id": profile.user_id,
                "name": profile.user.name,
                "email": profile.user.email,
            }
            for profile in profiles
        ]
