from django.db import models

class HomeSettings(models.Model):
    """Singleton model for Homepage settings"""
    # Hero Section
    hero_title = models.CharField(max_length=200, default="Dominate the Arena.")
    hero_subtitle = models.CharField(max_length=100, default="Combat Grade Engineering")
    hero_description = models.TextField(default="Precision-engineered combat robots and high-torque propulsion systems for professional robot combat leagues.")
    hero_image = models.ImageField(upload_to='site/hero/', null=True, blank=True)
    
    # Stats
    parts_shipped = models.CharField(max_length=50, default="2.4k+")
    tournaments_won = models.CharField(max_length=50, default="150+")
    
    # Visuals
    hologram_image = models.ImageField(upload_to='site/visuals/', null=True, blank=True, help_text="Image for the 'Why Choose Us' section")

    # CTA
    cta_title = models.CharField(max_length=200, default="Ready to Build?")
    cta_description = models.TextField(default="Join the league of professional builders today.")
    cta_btn_text = models.CharField(max_length=50, default="Enter the Arena")
    cta_btn_url = models.CharField(max_length=200, default="/shop/")

    class Meta:
        verbose_name = "Homepage Settings"
        verbose_name_plural = "Homepage Settings"

    def __str__(self):
        return "Homepage Configuration"
    
    def save(self, *args, **kwargs):
        if not self.pk and HomeSettings.objects.exists():
            # If you want to ensure only one exists, you can just return or raise error. 
            # For simplicity in admin, we usually just limit permissions or rely on user knowing its a singleton.
            # But here lets strictly enforce 1 instance if creating new.
            return
        return super(HomeSettings, self).save(*args, **kwargs)


class Feature(models.Model):
    """Features/Benefits listed on Homepage"""
    icon = models.CharField(max_length=50, help_text="Feather icon name (e.g., 'shield', 'zap')")
    title = models.CharField(max_length=100)
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title
