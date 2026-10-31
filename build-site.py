# Builds the installable website version of Six Again from six-again.html
import json, os, re, time
from PIL import Image, ImageDraw
import sys; SRC=sys.argv[1] if len(sys.argv)>1 else 'source-six-again.html'; OUT=sys.argv[2] if len(sys.argv)>2 else '.'
s=open(SRC).read()
ver=time.strftime('%Y%m%d%H%M')
head=f'''<!doctype html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no,viewport-fit=cover">
<meta name="description" content="Retro 9-a-side rugby league. Swipe to pass, kick and break the line.">
<meta name="theme-color" content="#0a130f">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Six Again">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" type="image/png" sizes="192x192" href="icon-192.png">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<script>window.SIX_STANDALONE=true;</script>
<style>:root{{color-scheme:dark;padding-top:env(safe-area-inset-top);padding-bottom:env(safe-area-inset-bottom)}}body{{margin:0;font:14px system-ui}}img{{max-width:100%}}[hidden]{{display:none!important}}html,body{{background:#0a130f}}</style>
</head>
<body>
'''
tail=f'''
<script>
if('serviceWorker' in navigator) window.addEventListener('load',()=>navigator.serviceWorker.register('sw.js').catch(()=>{{}}));
</script>
</body>
</html>
'''
open(f'{OUT}/index.html','w').write(head+s+tail)
manifest={"name":"Six Again","short_name":"Six Again","description":"Retro 9-a-side rugby league.","start_url":"./","scope":"./","display":"fullscreen","display_override":["fullscreen","standalone"],"orientation":"landscape","background_color":"#0a130f","theme_color":"#0a130f",
  "icons":[{"src":"icon-192.png","sizes":"192x192","type":"image/png","purpose":"any"},{"src":"icon-512.png","sizes":"512x512","type":"image/png","purpose":"any"},{"src":"icon-maskable-512.png","sizes":"512x512","type":"image/png","purpose":"maskable"}]}
open(f'{OUT}/manifest.webmanifest','w').write(json.dumps(manifest,indent=2))
sw=f'''// Six Again offline cache. Bump the version to ship an update.
const CACHE='six-again-{ver}';
const CORE=['./','index.html','manifest.webmanifest','icon-192.png','icon-512.png','apple-touch-icon.png'];
self.addEventListener('install',e=>{{ e.waitUntil(caches.open(CACHE).then(c=>c.addAll(CORE)).then(()=>self.skipWaiting())); }});
self.addEventListener('activate',e=>{{ e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim())); }});
self.addEventListener('fetch',e=>{{
  const r=e.request; if(r.method!=='GET') return;
  const page=r.mode==='navigate';
  // pages: network first so updates arrive, cache when offline. Everything else (fonts, icons): cache first.
  if(page){{ e.respondWith(fetch(r).then(res=>{{ const cp=res.clone(); caches.open(CACHE).then(c=>c.put('index.html',cp)); return res; }}).catch(()=>caches.match('index.html'))); return; }}
  e.respondWith(caches.match(r).then(hit=>hit||fetch(r).then(res=>{{ if(res.ok||res.type==='opaque'){{ const cp=res.clone(); caches.open(CACHE).then(c=>c.put(r,cp)); }} return res; }})));
}});
'''
open(f'{OUT}/sw.js','w').write(sw)
open(f'{OUT}/.nojekyll','w').write('')
# icons: a pixel-art amber jersey with a white 6 on the night-green pitch colour
def icon(size,pad):
    G=32; im=Image.new('RGB',(G,G),(10,19,15)); d=ImageDraw.Draw(im)
    A=(255,178,46); D=(168,100,0); W=(238,243,232); S=(217,160,102)
    o=pad
    d.rectangle([4+o,9,27-o,25],fill=A)            # body
    d.rectangle([1+o,9,6+o,15],fill=A); d.rectangle([25-o,9,30-o,15],fill=A)  # sleeves
    d.rectangle([1+o,16,3+o,18],fill=S); d.rectangle([28-o,16,30-o,18],fill=S)
    d.rectangle([12,8,19,10],fill=(10,19,15))      # neck
    d.rectangle([4+o,24,27-o,25],fill=D)
    six=["111","100","111","101","111"]            # digit 6, 3x5 cells of 2px
    for y,row in enumerate(six):
        for x,ch in enumerate(row):
            if ch=='1': d.rectangle([13+x*2,13+y*2,14+x*2,14+y*2],fill=W)
    return im.resize((size,size),Image.NEAREST)
icon(192,0).save(f'{OUT}/icon-192.png'); icon(512,0).save(f'{OUT}/icon-512.png'); icon(180,0).save(f'{OUT}/apple-touch-icon.png')
m=Image.new('RGB',(512,512),(10,19,15)); m.paste(icon(352,0),(80,80)); m.save(f'{OUT}/icon-maskable-512.png')
open(f'{OUT}/README.md','w').write('# Six Again\n\nRetro 9-a-side rugby league. Open the site, then use **Add to Home Screen** to play full screen.\n\nProgress saves on each device. Use **Backup & Restore** on the home screen to move a league between devices.\n')
print('built', sorted(os.listdir(OUT)))
