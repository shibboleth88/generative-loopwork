/* Generative loopwork — the rules of RULES.md, in JavaScript.
   A port of loopwork.py so the page can generate rather than replay. The
   solver here is the generator's (two-sided repulsion, gravity, per-tension
   rest lengths), not the handling one. Seeds do NOT match the Python build:
   the random streams differ, so the same seed gives a different piece of the
   same family. Everything that is a RULE is identical; only the noise differs. */

export const DEF = {
  seed:7, max_stitches:900,
  loop_capacity:3, clearance:0.65, tries:30, probes:40, turn:0.5, contact:1.9,
  strands:'KN', heavy_every:120, heavy_run:14, heavy_scale:2.8,
  target_policy:'window', join_rate:0.34, ladder_period:13, window:26, nearest_radius:1.15,
  ring_every:130, ring_radius:0.315, ring_tube:0.12, ring_weight:7.0,
  strand_runs_out:14, tail_stitches:13, tail_jitter:0.5, fringe_density:0.45,
  tension_var:0.45, tension_run:28, sprawl:0.0,
  cord_mm:8.0, cord_radius:0.05, loop_a:0.21, loop_b:0.125,
  ply:0, ply_depth:0.17, ply_period:0.45,
  wander:0.75, hand:0.22,
  repel_cut:1.25, tension_only:true, simulate_carries:true,
  settle_every:25, settle_iters:7, iters:160,
  gravity:0.0005, stiff_chain:0.30, repel:0.055, damping:0.80, max_step:0.22,
  rebuild_every:30,
};
export const TARGETS = {
  chain:   'never join; a pure 1-D chain (the L3-off control)',
  ladder:  'join to the stitch a fixed period back -> a tube of that girth',
  window:  'join to any stitch within the last N -> an irregular mesh',
  nearest: 'join to whatever loop is nearest in SPACE -> self-felting blob',
  random:  'join to any earlier stitch at all -> long-range tangle',
};
const MATS = { black:[0.085,0.085,0.095], natural:[0.93,0.89,0.80],
               heavy:[0.76,0.63,0.47], wood:[0.98,0.88,0.71] };

function rng32(a){ return function(){ a|=0; a=a+0x6D2B79F5|0;
  let t=Math.imul(a^a>>>15,1|a); t=t+Math.imul(t^t>>>7,61|t)^t;
  return ((t^t>>>14)>>>0)/4294967296; }; }
const norm3=(v)=>{ const L=Math.hypot(v[0],v[1],v[2])||1; return [v[0]/L,v[1]/L,v[2]/L]; };

function tensionOf(R,n,seed){
  const t=new Float32Array(n).fill(1);
  if(R.tension_var<=0) return t;
  const rnd=rng32(seed+991);
  let i=0;
  while(i<n){
    const run=Math.max(4, Math.round(R.tension_run*(0.65+0.7*rnd())));
    const lvl=Math.max(0.35, 1+R.tension_var*(rnd()-0.5)*2);
    for(let k=i;k<Math.min(n,i+run);k++) t[k]=lvl;
    i+=run;
  }
  return t;
}

/* L1-L9: the work */
export function work(R){
  const rnd=rng32(R.seed);
  const cap=R.max_stitches;
  const P=new Float32Array(cap*3);
  const target=new Int32Array(cap); for(let i=0;i<cap;i++) target[i]=i-1;
  const joined=new Uint8Array(cap), occ=new Int32Array(cap), dead=new Uint8Array(cap);
  const rings=[], tails=[], carries=[];
  const tens=tensionOf(R,cap,R.seed);
  const pitch=R.loop_a*1.15, clear=R.clearance*pitch;
  const cell=Math.max(clear,1e-6), ccell=Math.max(R.contact*pitch, cell);
  const grid=new Map(), cgrid=new Map();
  const key=(x,y,z,c)=>Math.floor(x/c)+','+Math.floor(y/c)+','+Math.floor(z/c);
  const add=(i)=>{
    const x=P[i*3],y=P[i*3+1],z=P[i*3+2];
    let k=key(x,y,z,cell); let b=grid.get(k); if(!b){b=[];grid.set(k,b);} b.push(i);
    k=key(x,y,z,ccell); b=cgrid.get(k); if(!b){b=[];cgrid.set(k,b);} b.push(i);
  };
  const rebuild=(upto)=>{ grid.clear(); cgrid.clear(); for(let i=0;i<upto;i++) add(i); };
  function free(px,py,pz,ex1,ex2,scale){
    const c2=(clear*scale)*(clear*scale);
    const kx=Math.floor(px/cell), ky=Math.floor(py/cell), kz=Math.floor(pz/cell);
    for(let dx=-1;dx<=1;dx++) for(let dy=-1;dy<=1;dy++) for(let dz=-1;dz<=1;dz++){
      const b=grid.get((kx+dx)+','+(ky+dy)+','+(kz+dz)); if(!b) continue;
      for(const j of b){ if(j===ex1||j===ex2) continue;
        const ex=P[j*3]-px, ey=P[j*3+1]-py, ez=P[j*3+2]-pz;
        if(ex*ex+ey*ey+ez*ez<c2) return false; }
    }
    return true;
  }
  function contactCount(px,py,pz){
    const kx=Math.floor(px/ccell), ky=Math.floor(py/ccell), kz=Math.floor(pz/ccell);
    let t=0;
    for(let dx=-1;dx<=1;dx++) for(let dy=-1;dy<=1;dy++) for(let dz=-1;dz<=1;dz++){
      const b=cgrid.get((kx+dx)+','+(ky+dy)+','+(kz+dz)); if(b) t+=b.length;
    }
    return t;
  }
  function pickTarget(i,gx,gy,gz){
    const p=R.target_policy;
    if(p==='chain') return i-1;
    if(p==='ladder') return Math.max(0,i-R.ladder_period);
    if(p==='window'){ const lo=Math.max(0,i-R.window);
      return (i-1>lo)? lo+Math.floor(rnd()*(i-1-lo)) : i-1; }
    if(p==='random') return Math.floor(rnd()*(i-1));
    if(p==='nearest'){
      if(i<10) return i-1;
      let best=-1,bd=R.nearest_radius*R.nearest_radius;
      for(let j=0;j<i-6;j++){ if(occ[j]>=R.loop_capacity) continue;
        const ex=P[j*3]-gx, ey=P[j*3+1]-gy, ez=P[j*3+2]-gz;
        const d2=ex*ex+ey*ey+ez*ez; if(d2<bd){bd=d2;best=j;} }
      return best>=0? best : i-1;
    }
    return i-1;
  }
  // a fair spread of directions for writing a loop off (L8)
  const PROBE=[]; { const g=Math.PI*(3-Math.sqrt(5));
    for(let k=0;k<R.probes;k++){ const z=1-2*(k+0.5)/R.probes, r=Math.sqrt(Math.max(0,1-z*z));
      PROBE.push([r*Math.cos(g*k), r*Math.sin(g*k), z]); } }
  function relocate(n){
    const live=[]; for(let j=0;j<n;j++) if(!dead[j] && occ[j]<R.loop_capacity) live.push(j);
    for(let s=live.length-1;s>0;s--){ const q=Math.floor(rnd()*(s+1)); [live[s],live[q]]=[live[q],live[s]]; }
    for(const j of live){
      for(const d of PROBE){
        const px=P[j*3]+pitch*d[0], py=P[j*3+1]+pitch*d[1], pz=P[j*3+2]+pitch*d[2];
        if(free(px,py,pz,j,-1,1)) return [j,px,py,pz,d];
      }
      dead[j]=1;
    }
    return null;
  }

  const vel=new Float32Array(cap*3), mass=new Float32Array(cap).fill(1);
  const linkRest=R.loop_a*0.95;
  let d=[1,0,0], n=1, ended='safety_bound';
  add(0);
  while(n<cap){
    let placed=false, best=null;
    for(let a=0;a<R.tries;a++){
      let dd;
      if(a>=R.tries*(1-R.turn)){ dd=norm3([rnd()*2-1,rnd()*2-1,rnd()*2-1]); }
      else { const sp=R.wander*(0.35+1.5*a/Math.max(1,R.tries-1));
        dd=norm3([d[0]+sp*(rnd()-0.5), d[1]+sp*(rnd()-0.5), d[2]+sp*(rnd()-0.5)-0.012]); }
      const lp=pitch*tens[n];
      const gx=P[(n-1)*3]+lp*dd[0]+R.hand*lp*(rnd()-0.5);
      const gy=P[(n-1)*3+1]+lp*dd[1]+R.hand*lp*(rnd()-0.5);
      const gz=P[(n-1)*3+2]+lp*dd[2]+R.hand*lp*(rnd()-0.5);
      let t=n-1;
      if(n>3 && rnd()<R.join_rate) t=pickTarget(n,gx,gy,gz);
      if(occ[t]>=R.loop_capacity){ if(occ[n-1]>=R.loop_capacity) continue; t=n-1; }
      const px=(t===n-1)?gx:0.45*gx+0.55*P[t*3];
      const py=(t===n-1)?gy:0.45*gy+0.55*P[t*3+1];
      const pz=(t===n-1)?gz:0.45*gz+0.55*P[t*3+2];
      if(!free(px,py,pz,n-1,t,tens[n])) continue;
      if(R.contact<=0 || rnd()<R.sprawl){ best=[0,px,py,pz,dd,t]; break; }
      const c=contactCount(px,py,pz);
      if(!best || c>best[0]) best=[c,px,py,pz,dd,t];
    }
    if(best){ const [,px,py,pz,dd,t]=best;
      P[n*3]=px; P[n*3+1]=py; P[n*3+2]=pz;
      target[n]=t; joined[n]=(t!==n-1)?1:0; occ[t]++; add(n); d=dd; placed=true; }
    if(!placed){
      const got=relocate(n);
      if(!got){ ended='saturated'; break; }
      const [t,px,py,pz,dd]=got;
      carries.push([n-1,n,Math.hypot(px-P[(n-1)*3],py-P[(n-1)*3+1],pz-P[(n-1)*3+2])]);
      P[n*3]=px; P[n*3+1]=py; P[n*3+2]=pz;
      target[n]=t; joined[n]=1; occ[t]++; add(n); d=dd;
    }
    if(R.ring_every && n%R.ring_every===0) rings.push(n);
    if(R.strand_runs_out && n%R.strand_runs_out===0) tails.push(n);
    n++;
    if(R.settle_every && n>4 && n%R.settle_every===0){
      mass.fill(1); for(const r of rings) if(r<n) mass[r]=R.ring_weight;
      solve(R,P,target,joined,carries,n,vel,R.settle_iters,pitch,linkRest,mass,tens);
      rebuild(n);
    }
  }
  tails.push(n-1);
  const colour=[];
  for(let i=0;i<n;i++) colour.push(R.strands[i%R.strands.length]==='K'?'black':'natural');
  if(R.heavy_every) for(let st=R.heavy_every; st<n; st+=R.heavy_every)
    for(let k=st;k<Math.min(n,st+R.heavy_run);k++) colour[k]='heavy';
  return {P:P.subarray(0,n*3), target, joined, occ, rings, tails, carries, colour,
          ended, tens:tens.subarray(0,n), n,
          dead:Array.from(dead.subarray(0,n)).reduce((a,b)=>a+b,0)};
}

/* L7: the same springs the generator uses */
export function solve(R,P,tgt,joined,carries,n,vel,iters,pitch,linkRest,mass,tens){
  const A=[],B=[],rest=[];
  for(let i=1;i<n;i++){ A.push(i); B.push(i-1); rest.push(pitch*(tens?tens[i]:1)); }
  for(let i=1;i<n;i++) if(joined[i]){ A.push(i); B.push(tgt[i]); rest.push(linkRest*(tens?tens[i]:1)); }
  if(R.simulate_carries) for(const [a,b,L] of carries) if(a<n&&b<n){ A.push(b); B.push(a); rest.push(L); }
  const cut=R.loop_a*R.repel_cut, cut2=cut*cut, capStep=R.max_step*pitch;
  const grid=new Map();
  for(let it=0; it<iters; it++){
    const F=new Float32Array(n*3);
    for(let e=0;e<A.length;e++){
      const a=A[e]*3,b=B[e]*3;
      const dx=P[a]-P[b], dy=P[a+1]-P[b+1], dz=P[a+2]-P[b+2];
      const L=Math.hypot(dx,dy,dz)||1e-9;
      const ext=R.tension_only? Math.max(0,L-rest[e]) : (L-rest[e]);
      if(ext===0) continue;
      const f=R.stiff_chain*ext/L;
      F[a]-=f*dx; F[a+1]-=f*dy; F[a+2]-=f*dz;
      F[b]+=f*dx; F[b+1]+=f*dy; F[b+2]+=f*dz;
    }
    if(it%R.rebuild_every===0){
      grid.clear();
      for(let i=0;i<n;i++){ const k=Math.floor(P[i*3]/cut)+','+Math.floor(P[i*3+1]/cut)+','+Math.floor(P[i*3+2]/cut);
        let b=grid.get(k); if(!b){b=[];grid.set(k,b);} b.push(i); }
    }
    for(const [k,b] of grid){
      const [gx,gy,gz]=k.split(',').map(Number);
      for(let dx2=0;dx2<=1;dx2++) for(let dy2=-1;dy2<=1;dy2++) for(let dz2=-1;dz2<=1;dz2++){
        if(dx2===0 && (dy2<0 || (dy2===0&&dz2<0))) continue;
        const nb=grid.get((gx+dx2)+','+(gy+dy2)+','+(gz+dz2)); if(!nb) continue;
        for(const i of b) for(const j of nb){ if(j<=i) continue;
          const a3=i*3,b3=j*3;
          const dx=P[a3]-P[b3], dy=P[a3+1]-P[b3+1], dz=P[a3+2]-P[b3+2];
          const d2=dx*dx+dy*dy+dz*dz;
          if(d2>=cut2||d2<1e-12) continue;
          const L=Math.sqrt(d2), o=R.repel*(cut-L)/L;
          F[a3]+=o*dx; F[a3+1]+=o*dy; F[a3+2]+=o*dz;
          F[b3]-=o*dx; F[b3+1]-=o*dy; F[b3+2]-=o*dz;
        }
      }
    }
    for(let i=0;i<n;i++){
      const i3=i*3; F[i3+2]-=R.gravity*mass[i];
      for(let k=0;k<3;k++){
        let v=R.damping*vel[i3+k]+F[i3+k];
        v=Math.max(-capStep,Math.min(capStep,v));
        vel[i3+k]=v; P[i3+k]+=v;
      }
    }
    P[0]=0; P[1]=0; P[2]=0;
  }
  return P;
}

/* ---- geometry: the same shapes the Python exporter makes ---- */
const V=(a,b,c)=>[a,b,c];
function framesAt(P,i,n){
  const a=Math.max(0,i-1), b=Math.min(n-1,i+1);
  let T=norm3([P[b*3]-P[a*3],P[b*3+1]-P[a*3+1],P[b*3+2]-P[a*3+2]]);
  let up=[0,0,1];
  if(Math.abs(T[0]*up[0]+T[1]*up[1]+T[2]*up[2])>0.92) up=[1,0,0];
  const Lv=norm3([T[1]*up[2]-T[2]*up[1], T[2]*up[0]-T[0]*up[2], T[0]*up[1]-T[1]*up[0]]);
  const N=[Lv[1]*T[2]-Lv[2]*T[1], Lv[2]*T[0]-Lv[0]*T[2], Lv[0]*T[1]-Lv[1]*T[0]];
  return [T,Lv,N];
}
function bight(R,P,i,n,seg,scale){
  const [T,Lv,N]=framesAt(P,i,n);
  const X=(i%2===0)?Lv:N, out=[];
  for(let k=0;k<seg;k++){
    const a=2*Math.PI*k/seg, ca=Math.cos(a)*R.loop_a*scale, sa=Math.sin(a)*R.loop_b*scale;
    out.push([P[i*3]+ca*T[0]+sa*X[0], P[i*3+1]+ca*T[1]+sa*X[1], P[i*3+2]+ca*T[2]+sa*X[2]]);
  }
  return out;
}
function carryPath(P,a,b,seg=9){
  const L=Math.hypot(P[b*3]-P[a*3],P[b*3+1]-P[a*3+1],P[b*3+2]-P[a*3+2]);
  const mid=[0.5*(P[a*3]+P[b*3]), 0.5*(P[a*3+1]+P[b*3+1]), 0.5*(P[a*3+2]+P[b*3+2])-0.06*L];
  const out=[];
  for(let k=0;k<seg;k++){ const t=k/(seg-1), u=1-t;
    out.push([u*u*P[a*3]+2*u*t*mid[0]+t*t*P[b*3],
              u*u*P[a*3+1]+2*u*t*mid[1]+t*t*P[b*3+1],
              u*u*P[a*3+2]+2*u*t*mid[2]+t*t*P[b*3+2]]); }
  return out;
}
function tailPaths(R,w){
  const rnd=rng32(R.seed+1), out=[], P=w.P, n=w.n, pitch=R.loop_a*1.15;
  for(const s of w.tails){
    const i=Math.min(s,n-1), [T,Lv]=framesAt(P,i,n);
    for(const side of [-1,1]){
      const k=Math.max(3, Math.round(R.tail_stitches*(1-R.tail_jitter*rnd())));
      let p=[P[i*3],P[i*3+1],P[i*3+2]];
      let d=norm3([side*0.5*Lv[0], side*0.5*Lv[1], side*0.5*Lv[2]-1]);
      const path=[p.slice()];
      for(let q=0;q<k;q++){
        d=norm3([d[0]+0.22*(rnd()-0.5), d[1]+0.22*(rnd()-0.5), d[2]+0.22*(rnd()-0.5)-0.55]);
        p=[p[0]+pitch*1.25*d[0], p[1]+pitch*1.25*d[1], p[2]+pitch*1.25*d[2]];
        path.push(p.slice());
      }
      out.push({path, at:i, colour:w.colour[i]});
    }
  }
  return out;
}
function occlusion(R,w,floor=0.42){
  const P=w.P, n=w.n, r=R.loop_a*3.2, r2=r*r, cell=r, grid=new Map();
  for(let i=0;i<n;i++){ const k=Math.floor(P[i*3]/cell)+','+Math.floor(P[i*3+1]/cell)+','+Math.floor(P[i*3+2]/cell);
    let b=grid.get(k); if(!b){b=[];grid.set(k,b);} b.push(i); }
  const cnt=new Float32Array(n);
  for(let i=0;i<n;i++){
    const kx=Math.floor(P[i*3]/cell), ky=Math.floor(P[i*3+1]/cell), kz=Math.floor(P[i*3+2]/cell);
    let c=0;
    for(let dx=-1;dx<=1;dx++) for(let dy=-1;dy<=1;dy++) for(let dz=-1;dz<=1;dz++){
      const b=grid.get((kx+dx)+','+(ky+dy)+','+(kz+dz)); if(!b) continue;
      for(const j of b){ const ex=P[j*3]-P[i*3], ey=P[j*3+1]-P[i*3+1], ez=P[j*3+2]-P[i*3+2];
        if(ex*ex+ey*ey+ez*ez<r2) c++; }
    }
    cnt[i]=c-1;
  }
  const idx=Array.from({length:n},(_,i)=>i).sort((a,b)=>cnt[a]-cnt[b]);
  const sh=new Float32Array(n);
  idx.forEach((i,rank)=>{ const o=rank/Math.max(1,n-1);
    sh[i]=floor+(1-floor)*Math.pow(1-o,0.85); });
  return sh;
}

export function build(R){
  const t0=performance.now();
  const w=work(R);
  const n=w.n, P=w.P;
  const mass=new Float32Array(n).fill(1);
  for(const r of w.rings) if(r<n) mass[r]=R.ring_weight;
  solve(R,P,w.target,w.joined,w.carries,n,new Float32Array(n*3),R.iters,
        R.loop_a*1.15, R.loop_a*0.95, mass, w.tens);
  const sh=occlusion(R,w);
  const rad=(c)=>R.cord_radius*(c==='heavy'?R.heavy_scale:1);
  const r3=(a)=>a.map(p=>[+p[0].toFixed(4),+p[1].toFixed(4),+p[2].toFixed(4)]);

  const stitches=[];
  for(let i=0;i<n;i++) stitches.push({at:i, colour:w.colour[i], shade:+sh[i].toFixed(3),
    t:w.target[i], radius:rad(w.colour[i]), pts:r3(bight(R,P,i,n,12,w.tens[i]))});
  const carries=w.carries.map(([a,b])=>({at:b, colour:w.colour[b], shade:+sh[b].toFixed(3),
    radius:rad(w.colour[b]), pts:r3(carryPath(P,a,b))}));
  const tails=tailPaths(R,w).map(t=>({at:t.at, colour:t.colour, shade:+sh[Math.min(t.at,n-1)].toFixed(3),
    radius:rad(t.colour), pts:r3(t.path)}));
  const rings=w.rings.map(s=>{ const [T]=framesAt(P,s,n);
    return {at:s, c:[P[s*3],P[s*3+1],P[s*3+2]], axis:T, r:R.ring_radius, tube:R.ring_tube}; });

  let mn=[1e9,1e9,1e9], mx=[-1e9,-1e9,-1e9];
  for(let i=0;i<n;i++) for(let k=0;k<3;k++){ const v=P[i*3+k]; if(v<mn[k])mn[k]=v; if(v>mx[k])mx[k]=v; }
  const bb=mx.map((v,k)=>v-mn[k]);
  const cm=R.cord_mm/10/(2*R.cord_radius);
  let joins=0, full=0, occmax=0;
  for(let i=0;i<n;i++){ joins+=w.joined[i]; if(w.occ[i]>=R.loop_capacity) full++; occmax=Math.max(occmax,w.occ[i]); }
  const stats={stitches:n, ended:w.ended, max_occupancy:occmax, full_loops:full,
    dead_loops:w.dead, joins, carries:w.carries.length, rings:w.rings.length,
    tail_ends:2*w.tails.length, policy:R.target_policy,
    bbox:bb.map(v=>+v.toFixed(3)), cm_per_unit:+cm.toFixed(3),
    size_cm:bb.map(v=>+(v*cm).toFixed(1)),
    aspect:+(Math.max(...bb)/Math.max(1e-9,Math.min(...bb))).toFixed(2),
    strand_m:R.strand_runs_out? +(R.strand_runs_out*1.069*cm/100).toFixed(2):null,
    build_seconds:+((performance.now()-t0)/1000).toFixed(3)};

  return {ruleset:{...R}, stats, policies:TARGETS, materials:MATS,
    stitches, carries, tails, rings,
    handling:{ target:Array.from(w.target.subarray(0,n)),
      joined:Array.from(w.joined.subarray(0,n)),
      carries:w.carries.map(([a,b])=>[a,b]), rings:w.rings,
      pitch:R.loop_a*1.15, link_rest:R.loop_a*0.95, cutoff:R.loop_a*1.6,
      stiff_chain:R.stiff_chain, repel:R.repel, gravity:R.gravity,
      damping:R.damping, max_step:R.max_step, ring_weight:R.ring_weight }};
}
