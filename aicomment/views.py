from django.shortcuts import render
from django.http import JsonResponse
from .models import Book, FileUpload
from .utils import generate_response_for_user
from .forms import FileUploadForm

def upload_file(request):
    if request.method == 'POST' and request.FILES['file']:
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'File uploaded successfully!'})
    else:
        form = FileUploadForm()
    return render(request, 'upload_file.html', {'form': form})

def ai_search(request):
    if request.method == 'GET' and 'file_id' in request.GET and 'query' in request.GET:
        file_id = request.GET['file_id']
        query = request.GET['query']
        response = generate_response_for_user(file_id, query)
        return JsonResponse({"response": response})
    return render(request, 'ai_search.html')
