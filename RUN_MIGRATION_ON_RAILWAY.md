# How to Run Migration on Railway

Since Railway CLI isn't installed, we'll use Railway's web interface to run the migration command.

## Option 1: Railway Web Shell (Easiest)

1. Go to **Railway Dashboard** → Your backend project
2. Click on the **backend service**
3. Look for **"Shell"** or **"Terminal"** tab (might be under Settings or in the service menu)
4. Once in the shell, run:
   ```bash
   python manage.py download_wishlist_images --rescrape
   ```

## Option 2: One-off Command (If Shell not available)

If Railway doesn't have a shell tab, you can trigger it via their API or use a temporary command in the Procfile:

1. Temporarily modify `backend/Procfile` to run the migration:
   ```
   web: python manage.py download_wishlist_images --rescrape && python manage.py collectstatic --noinput && python manage.py migrate && gunicorn backend.wsgi
   ```

2. Commit and push
3. Wait for deployment
4. **IMPORTANT:** Revert the Procfile back to normal:
   ```
   web: python manage.py collectstatic --noinput && python manage.py migrate && gunicorn backend.wsgi
   ```

## Option 3: Create a Management Command Endpoint (Dev Only)

Temporarily add an API endpoint that runs the migration when called:

1. Add to `backend/core/views.py`:
   ```python
   from rest_framework.decorators import api_view, permission_classes
   from rest_framework.permissions import AllowAny
   from rest_framework.response import Response
   from django.core.management import call_command
   from io import StringIO

   @api_view(['POST'])
   @permission_classes([AllowAny])  # REMOVE THIS IN PRODUCTION!
   def run_migration(request):
       out = StringIO()
       call_command('download_wishlist_images', '--rescrape', stdout=out)
       return Response({'output': out.getvalue()})
   ```

2. Add to `backend/backend/urls.py`:
   ```python
   path('api/run-migration/', views.run_migration),
   ```

3. Deploy, then call: `curl -X POST https://gift-sync-production.up.railway.app/api/run-migration/`

4. **REMOVE THE ENDPOINT** after migration completes

## Recommended: Option 1 (Railway Shell)

The cleanest way is to use Railway's built-in shell. Check if your Railway project has this feature enabled.
