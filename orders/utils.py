# orders/utils.py
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.pdfgen import canvas
from io import BytesIO
from django.conf import settings
from datetime import datetime


def generate_invoice_pdf(order):
    """
    Génère un PDF de facture pour une commande
    """
    buffer = BytesIO()
    
    # Créer le document PDF
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    # Conteneur pour les éléments du PDF
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=30,
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=12,
    )
    
    normal_style = styles['Normal']
    
    # En-tête de la facture
    title = Paragraph(f"FACTURE N° {order.id}", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.5*cm))
    
    # Informations de l'entreprise et du client
    info_data = [
        ['ZOONOVA', f'Client: {order.full_name}'],
        ['Adresse de l\'entreprise', f'Email: {order.email}'],
        ['Email: contact@ZOONOVA.com', f'Tél: {order.phone}'],
        ['', ''],
        [f'Date: {order.created_at.strftime("%d/%m/%Y")}'],
    ]
    
    if order.tracking_number:
        info_data.append(['', f'Suivi: {order.tracking_number}'])
    
    info_table = Table(info_data, colWidths=[8*cm, 8*cm])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2c3e50')),
        ('FONTNAME', (0, 0), (0, 2), 'Helvetica-Bold'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 1*cm))
    
    # Adresse de livraison
    shipping_heading = Paragraph("Adresse de livraison", heading_style)
    elements.append(shipping_heading)
    
    shipping_address = Paragraph(
        f"{order.full_address}",
        normal_style
    )
    elements.append(shipping_address)
    elements.append(Spacer(1, 1*cm))
    
    # Tableau des articles
    items_heading = Paragraph("Articles commandés", heading_style)
    elements.append(items_heading)
    elements.append(Spacer(1, 0.3*cm))
    
    # En-tête du tableau
    items_data = [
        ['Article', 'Quantité', 'Prix unitaire', 'Sous-total']
    ]
    
    # Lignes des articles
    for item in order.items.all():
        items_data.append([
            item.book_title,
            str(item.quantity),
            f"{item.unit_price / 100:.2f} €",
            f"{item.subtotal / 100:.2f} €"
        ])
    
    # Totaux
    items_data.append(['', '', 'Sous-total:', f"{order.subtotal / 100:.2f} €"])
    items_data.append(['', '', 'Frais de port:', f"{order.shipping_cost / 100:.2f} €"])
    items_data.append(['', '', 'TOTAL:', f"{order.total / 100:.2f} €"])
    
    items_table = Table(items_data, colWidths=[8*cm, 2*cm, 3*cm, 3*cm])
    items_table.setStyle(TableStyle([
        # En-tête
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        
        # Corps du tableau
        ('FONTNAME', (0, 1), (-1, -4), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -4), 10),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        
        # Lignes des totaux
        ('FONTNAME', (0, -3), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -3), (-1, -1), 11),
        ('LINEABOVE', (0, -3), (-1, -3), 1, colors.grey),
        ('LINEABOVE', (0, -1), (-1, -1), 2, colors.black),
        
        # Bordures
        ('GRID', (0, 0), (-1, -4), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    elements.append(items_table)
    elements.append(Spacer(1, 2*cm))
    
    # Pied de page
    footer = Paragraph(
        "Merci pour votre commande !<br/>"
        "Pour toute question, contactez-nous à contact@ZOONOVA.com",
        ParagraphStyle(
            'Footer',
            parent=normal_style,
            fontSize=9,
            textColor=colors.grey,
            alignment=1  # Centré
        )
    )
    elements.append(footer)
    
    # Construire le PDF
    doc.build(elements)
    
    # Récupérer le contenu du PDF
    pdf = buffer.getvalue()
    buffer.close()
    
    return pdf