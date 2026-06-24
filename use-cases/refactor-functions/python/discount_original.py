def discount(cart,promos,user):
    d=0;tot=0
    for i in cart:tot+=i['price']*i['quantity']
    for p in promos:
        if p['type']=='percent' and (p['min_purchase'] is None or tot>=p['min_purchase']):val=tot*p['value']/100;d=max(d,val)
        elif p['type']=='fixed' and (p['min_purchase'] is None or tot>=p['min_purchase']):val=min(p['value'],tot);d=max(d,val)
        elif p['type']=='shipping' and tot>=p['min_purchase']:user['free_shipping']=True
    if user['status']=='vip':vd=tot*0.05;d=max(d,vd)
    elif user['status']=='member' and user['months']>6:vd=tot*0.02;d=max(d,vd)
    return {'original':tot,'discount':d,'final':tot-d,'free_shipping':user.get('free_shipping',False)}
