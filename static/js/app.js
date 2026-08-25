document.addEventListener("DOMContentLoaded",()=>{
  const menuButton=document.querySelector("[data-menu]");
  const nav=document.querySelector("[data-nav]");
  const searchPanel=document.querySelector("[data-search-panel]");
  const openSearch=()=>{if(!searchPanel)return;searchPanel.hidden=false;document.body.style.overflow="hidden";searchPanel.querySelector("input")?.focus()};
  const closeSearch=()=>{if(!searchPanel)return;searchPanel.hidden=true;document.body.style.overflow=""};
  menuButton?.addEventListener("click",()=>{const open=nav?.classList.toggle("nav-open");menuButton.setAttribute("aria-expanded",String(Boolean(open)))});
  document.querySelector("[data-search-open]")?.addEventListener("click",openSearch);
  document.querySelector("[data-search-close]")?.addEventListener("click",closeSearch);
  document.addEventListener("keydown",event=>{if(event.key==="Escape")closeSearch();if(event.key==="/"&&!event.metaKey&&!event.ctrlKey&&!["INPUT","TEXTAREA","SELECT"].includes(document.activeElement?.tagName||"")){event.preventDefault();openSearch()}});
  document.querySelectorAll(".flash button").forEach(button=>button.addEventListener("click",()=>button.parentElement?.remove()));
  const observer=new IntersectionObserver(entries=>entries.forEach(entry=>entry.target.classList.toggle("is-visible",entry.isIntersecting)),{threshold:.12});
  document.querySelectorAll(".game-card,.trade-grid>a,.editorial article,.news-grid>a").forEach(card=>observer.observe(card));
  document.querySelectorAll("[data-game-preview]").forEach(player=>{
    const video=player.querySelector("video");
    const control=player.querySelector(".fs-preview-control,.fs-detail-control");
    const icon=control?.querySelector("i");
    const label=control?.querySelector("b");
    const note=control?.querySelector("small");
    const originalLabel=player.getAttribute("aria-label")||"Play video preview";
    const prepare=()=>{if(video&&!video.src&&video.dataset.src){video.src=video.dataset.src;video.load()}};
    const setState=playing=>{
      video?.classList.toggle("is-playing",playing);
      player.setAttribute("aria-pressed",String(playing));
      player.setAttribute("aria-label",playing?originalLabel.replace(/^Play/,"Pause"):originalLabel.replace(/^Pause/,"Play"));
      if(icon)icon.textContent=playing?"Ⅱ":"▶";
      if(label)label.textContent=playing?"Preview playing":player.classList.contains("fs-detail-player")?"Play game preview":"Touch to preview";
      if(note)note.textContent=playing?"Tap to pause":player.classList.contains("fs-detail-player")?"Muted presentation footage":"Video · sound off";
    };
    const play=()=>{if(!video)return;prepare();video.play().then(()=>setState(true)).catch(()=>setState(false))};
    const stop=()=>{if(!video)return;video.pause();video.currentTime=0;setState(false)};
    player.addEventListener("pointerenter",event=>{if(event.pointerType==="mouse")play()});
    player.addEventListener("pointerleave",event=>{if(event.pointerType==="mouse")stop()});
    player.addEventListener("focus",()=>{if(player.matches(":focus-visible"))play()});
    player.addEventListener("blur",stop);
    player.addEventListener("click",()=>video?.paused?play():stop());
  });
});
