from django.http import HttpResponse
from django.template.loader import get_template

def generate_donation_pdf(donations, filename):
    """
    Generate a donation history export
    
    Note: Currently returns HTML instead of PDF due to dependency issues
    """
    template = get_template('donations/donation_history.html')
    context = {
        'donations': donations,
        'pdf_mode': True
    }
    html = template.render(context)
    
    # Return formatted HTML for now
    response = HttpResponse(html, content_type='text/html')
    response['Content-Disposition'] = f'inline; filename="{filename}.html"'
    
    return response
