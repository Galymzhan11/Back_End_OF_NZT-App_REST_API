from django.utils import timezone

class UpdateLastActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            user = request.user
            current_time = timezone.now()
            
            
            if user.last_activity_time:
                
                session_duration = (current_time - user.last_activity_time).total_seconds() / 3600
                
                
                user.all_time_activity += session_duration

           
            user.last_activity_time = current_time
            user.save()

        response = self.get_response(request)
        return response