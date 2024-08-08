from django.db import models

# Create your models here.
class Berita(models.Model):
    link = models.URLField() 
    portal = models.CharField(max_length=50)
    judul = models.CharField(max_length=255)
    konten = models.TextField()
    jumlah_komentar = models.PositiveIntegerField()
    timestamp_scrape = models.DateTimeField(verbose_name='Timestamp Scrape')

    @property
    def status_prediksi(self):
        return all(komentar.prediksi is not None for komentar in self.komentar_set.all())
    
    def __str__(self):
        return self.judul

class Komentar(models.Model):
    berita = models.ForeignKey(Berita, on_delete=models.CASCADE, related_name='komentar_set')
    penulis_komentar = models.CharField(max_length=255)
    isi_komentar = models.TextField()
    prediksi = models.CharField(max_length=10, blank=True, null=True)
    probabilitas = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f'{self.penulis_komentar}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.berita.jumlah_komentar = Komentar.objects.filter(berita=self.berita).count()
        self.berita.save()

    @property
    def formatted_probabilitas(self):
        if self.probabilitas is not None:
            return "{:.4%}".format(self.probabilitas)
        else:
            return "N/A"
    
    @property
    def prediksi_seharusnya(self):
        if self.prediksi == "Hate":
            return "Non-Hate"
        else:
            return "Hate"