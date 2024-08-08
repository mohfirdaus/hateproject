from django.shortcuts import render, redirect, get_object_or_404
from .forms import LinkBeritaForm, BeritaSearchForm
from .scraper_kompas import scraper_kompas
from .scraper_detik import scraper_detik
from .scraper_cnn import scraper_cnn
from .models import Berita, Komentar
import logging
from urllib.parse import urlparse, urlunparse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .modelprediction import prediction
from django.utils import timezone
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import StreamingHttpResponse


logger = logging.getLogger(__name__)

def berita(request):
    # berita_list = Berita.objects.all()
    berita_list = Berita.objects.order_by('-timestamp_scrape')[:5]

    for berita in berita_list:
        # print(f'Judul: {berita.judul}, Timestamp Scrape: {berita.timestamp_scrape}')
        print("aaaaa")

    if request.method == 'POST':
        form = LinkBeritaForm(request.POST)
        if form.is_valid():
            link_berita = form.cleaned_data['link']
            print(link_berita)

             # Validate if the input is a valid URL
            if not link_berita.startswith("https://"):
                form = LinkBeritaForm()
                # request.stop_prediction = True
                return render(request, 'home.html', {'berita_list': berita_list, 'form': form, 'error_message': f'Invalid link','stop_prediction': True})
            
            link_berita = link_berita.replace('http://', 'https://') if link_berita.startswith('http://') else ('https://' + link_berita) if link_berita.startswith('www.') else ('https://' + link_berita) if not link_berita.startswith('https://') else link_berita
            parsed_url = urlparse(link_berita)
            link_berita = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, '', '', ''))

            # Check if the link already exists in the database
            if Berita.objects.filter(link=link_berita).exists():
                form = LinkBeritaForm()
                # request.stop_prediction = True
                return render(request, 'home.html', {'berita_list': berita_list, 'form': form, 'error_message': 'This link has already been scraped.', 'stop_prediction': True})
            
            try:
                parsed_url = urlparse(link_berita)
                domain = parsed_url.netloc

                # Ensure the link is scraped based on the scraper function of the respective news website
                if 'kompas.com' in domain:
                    scraper_function = scraper_kompas
                    portal = "Kompas.com"
                elif 'detik.com' in domain:
                    scraper_function = scraper_detik
                    portal = "Detik.com"
                elif 'cnnindonesia.com' in domain:
                    scraper_function = scraper_cnn
                    portal = "CNNIndonesia.com"
                else:
                    raise ValueError('Unsupported news website')
                
                # Run the scraping function based on the news portal's domain
                scraped_data = scraper_function(link_berita)
                print(scraped_data)

                if scraped_data and scraped_data['jumlah_komentar'] > 0:
                    # Input link, title, content, and number of comments into the Berita model
                    berita_baru = Berita.objects.create(
                        link=scraped_data['link'],
                        judul=scraped_data['judul'],
                        konten=scraped_data['konten'],
                        jumlah_komentar=scraped_data['jumlah_komentar'],
                        portal=portal,
                        timestamp_scrape=timezone.now()
                    )

                    # Input comments into the Komentar model
                    for komentar_data in scraped_data.get('komentar', []):
                        Komentar.objects.create(
                            berita=berita_baru,
                            penulis_komentar=komentar_data['username'],
                            isi_komentar=komentar_data['komentar']
                        )

                    # Redirect to the detail page if the news and comments are successfully scraped
                    # request.stop_prediction = True
                    return redirect('detail_berita', berita_id=berita_baru.id) 

                else:
                    error_message = "There are no comments that can be scraped"
                    form = LinkBeritaForm()
                    # request.stop_prediction = True
                    return render(request, 'home.html', {'berita_list': berita_list, 'form': form, 'error_message': error_message, 'stop_prediction': True})

            # Handle the error if scraping fails
            except Exception as e:
                error_message = f'Error in scraping: {e}'
                form = LinkBeritaForm()
                # request.stop_prediction = True
                return render(request, 'home.html', {'berita_list': berita_list, 'form': form, 'error_message': error_message, 'stop_prediction': True})
    else:
        form = LinkBeritaForm()
    # request.stop_prediction = True
    return render(request, 'home.html', {'berita_list': berita_list, 'form': form, 'stop_prediction': True})


def detail_berita(request, berita_id,):
    try:
        hasil_scrape = Berita.objects.get(id=berita_id)
        komentar_list = Komentar.objects.filter(berita=hasil_scrape)
    except Berita.DoesNotExist:
        hasil_scrape = None
        komentar_list = None

    # Calculate counts
    hate_count = komentar_list.filter(prediksi='Hate').count()
    non_hate_count = komentar_list.filter(prediksi='Non-Hate').count()

    # Pagination
    paginator = Paginator(komentar_list, 10)  
    page = request.GET.get('page')

    try:
        komentar = paginator.page(page)
    except PageNotAnInteger:
        komentar = paginator.page(1)
    except EmptyPage:
        komentar = paginator.page(paginator.num_pages)
    
    filtered_komentar = [k for k in komentar if k.prediksi is None]

    return render(request, 'detail_berita.html', {'hasil_scrape': hasil_scrape, 'komentar': komentar, 'filtered_komentar': filtered_komentar, 'hate_count':hate_count, 'non_hate_count':non_hate_count})

def list_berita(request):
    form = BeritaSearchForm(request.GET)
    berita_list = Berita.objects.order_by('-timestamp_scrape')

    # Pencarian
    if form.is_valid():
        search_query = form.cleaned_data['search']
        if search_query:
            berita_list = berita_list.filter(
                Q(judul__icontains=search_query) |
                Q(portal__icontains=search_query) |
                Q(konten__icontains=search_query)
            )

    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(berita_list, 5)

    try:
        berita = paginator.page(page)
    except PageNotAnInteger:
        berita = paginator.page(1)
    except EmptyPage:
        berita = paginator.page(paginator.num_pages)

    return render(request, 'list_berita.html', {'berita_list': berita, 'berita': berita, 'form': form})

def predict_comments(request, berita_id):
    berita = Berita.objects.get(id=berita_id)
    # model_path = "model"
    # tokenizer_path = "tokenizer"

    predictions = prediction(request, berita_id)

    # Function to stream predictions
    def stream_predictions(predictions):
        for comment_prediction in predictions:
            # Convert prediction to bytes (adjust as per your requirement)
            prediction_bytes = str(comment_prediction).encode('utf-8')
            yield prediction_bytes

    # Create a StreamingHttpResponse with the streaming iterator
    response = StreamingHttpResponse(stream_predictions(predictions), content_type='application/octet-stream')

    # Optionally, you can set additional response headers or modify the response here

    # Redirect to the detail view after streaming the predictions
    return redirect('detail_berita', berita_id=berita_id)

def delete_berita(request, berita_id):
    berita = get_object_or_404(Berita, id=berita_id)

    if request.method == 'POST':
        berita.delete()
        messages.success(request, f'Berita "{berita.judul}" berhasil dihapus.') 
        return redirect('list_berita')

    return render(request, 'list_berita.html', {'berita': berita})

def login_view(request):
    if request.user.is_authenticated:
        messages.info(request, 'Anda sudah login.')
        return redirect('berita')
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('berita')
        else:
            messages.error(request, 'Username atau password salah.')

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Anda telah berhasil Logout!')
    return redirect('berita')
