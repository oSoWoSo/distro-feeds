(self.webpackChunk_N_E=self.webpackChunk_N_E||[]).push([[147],{4147:(e,t,s)=>{Promise.resolve().then(s.bind(s,5224))},5224:(e,t,s)=>{"use strict";s.d(t,{Page:()=>E});var a=s(5155),r=s(2115),n=s(6046),i=s(6680),l=s(8979);let o=e=>{let{className:t,content:s,selectBack:n}=e,o=null;return(0,r.useEffect)(()=>{o&&o.scrollTo(0,0)},[s]),(0,a.jsxs)("article",{ref:e=>{o=e},className:"pb-4 max-w-full break-words flex-grow p-6 xl:overflow-auto overscroll-contain ".concat(t),children:[(0,a.jsx)("a",{className:"cursor-pointer xl:hidden",onClick:n,children:"← Back"}),s&&(0,a.jsxs)("div",{children:[(0,a.jsx)("h2",{children:(0,a.jsx)("a",{className:"font-serif font-bold no-underline hover:underline",href:s.url,target:"_blank",rel:"noopener noreferrer",children:s.title})}),(0,a.jsxs)("div",{className:"xl:hidden",children:[(0,a.jsxs)("strong",{children:["From ",s.siteTitle]}),(0,a.jsxs)("span",{children:[","," ",(0,i.B)(1e3*s.timestamp,new Date,{addSuffix:!0})]})]}),(0,a.jsx)("div",{children:(0,l.Ay)(s.content,{replace:e=>(e.attribs&&"a"===e.name&&(e.attribs.target="_blank",e.attribs.rel="noopener noreferrer"),e)})})]}),(0,a.jsx)("div",{className:"pb-8"})]})};class c{async getCategories(){let e=await fetch("".concat(this.basePath,"/categories.json"));if(200!==e.status)throw Error("Fail to load categories");return(await e.json()).map(e=>({title:e.name,totalEntries:e.totalEntries,sites:e.sites.map(e=>({key:e.siteHash,title:e.title,totalEntries:e.totalEntries}))}))}async getCategoryEntries(e){arguments.length>1&&void 0!==arguments[1]&&arguments[1];let t=await fetch("".concat(this.basePath,"/categories/").concat(e,".json"));if(200!==t.status)throw Error("Fail to load category entries");return(await t.json()).map(e=>({key:e.entryHash,title:e.title,site:{key:e.siteHash,title:e.siteTitle},timestamp:Math.floor(e.date/1e3)}))}async getSiteEntries(e){arguments.length>1&&void 0!==arguments[1]&&arguments[1];let t=await fetch("".concat(this.basePath,"/sites/").concat(e,".json"));if(200!==t.status)throw Error("Fail to load site entries");return(await t.json()).entries.map(e=>({key:e.entryHash,title:e.title,site:{key:e.siteHash,title:e.siteTitle},timestamp:Math.floor(e.date/1e3)}))}async countAllEntries(){let e=await fetch("".concat(this.basePath,"/categories.json"));if(200!==e.status)throw Error("Fail to load count all entries");return(await e.json()).reduce((e,t)=>e+t.totalEntries,0)}async countSiteEntries(e){let t=await fetch("".concat(this.basePath,"/sites/").concat(e,".json"));if(200!==t.status)throw Error("Fail to load site entries");return(await t.json()).entries.length}async countCategoryEntries(e){let t=await fetch("".concat(this.basePath,"/categories/").concat(e,".json"));if(200!==t.status)throw Error("Fail to load category entries");return(await t.json()).length}async getAllEntries(){arguments.length>0&&void 0!==arguments[0]&&arguments[0];let e=await fetch("".concat(this.basePath,"/all.json"));if(200!==e.status)throw Error("Fail to load all entries");return(await e.json()).map(e=>({key:e.entryHash,title:e.title,site:{key:e.siteHash,title:e.siteTitle},timestamp:Math.floor(e.date/1e3)}))}async getContent(e){let t=await fetch("".concat(this.basePath,"/entries/").concat(e,".json"));if(200!==t.status)throw Error("Fail to load content");let s=await t.json();return{title:s.title,content:s.content,url:s.link,siteKey:s.siteHash,siteTitle:s.siteTitle,timestamp:Math.floor(s.date/1e3)}}constructor(e){this.basePath="".concat(e,"/data")}}s(4783);let u=null,d=e=>(u||(u=new c(e)),u),h=e=>{let{index:t,entry:s,selectedEntryHash:r,selectEntry:n,selectSite:l,entryRef:o}=e;return(0,a.jsxs)("div",{id:"entry-".concat(s.key),ref:o,className:"rounded px-4 ".concat(r===s.key&&"bg-gray-200"||"").trim(),children:[(0,a.jsx)("h3",{children:(0,a.jsxs)("a",{className:"font-serif no-underline hover:underline cursor-pointer",onClick:()=>n&&n(s.key),children:[t+1,". ",s.title]})}),(0,a.jsxs)("small",{children:[(0,a.jsx)("a",{className:"cursor-pointer",onClick:()=>l&&l(s.site.key),children:s.site.title}),s.timestamp&&(0,a.jsxs)("span",{children:[","," ",(0,i.B)(1e3*s.timestamp,new Date,{addSuffix:!0})]})]})]})},y=e=>{let{className:t,basePath:s,locationState:n,selectEntry:i,selectSite:l,selectBack:o}=e,[c,u]=(0,r.useState)("loading"),[y,f]=(0,r.useState)(""),[m,g]=(0,r.useState)([]),[p,w]=(0,r.useState)(0),[x,j]=(0,r.useState)(""),[k,E]=(0,r.useState)(0),b=(0,r.useRef)(null),v=null,N=async function(e,t){let s=arguments.length>2&&void 0!==arguments[2]?arguments[2]:0,a=d(e);switch(t.type){case"category":{let e=t.category,[r,n]=await Promise.all([a.getCategoryEntries(e,s),a.countCategoryEntries(e)]);return{entries:r,totalEntry:n}}case"site":{let{siteKey:e}=t,[r,n]="all"===e?await Promise.all([a.getAllEntries(s),a.countAllEntries()]):await Promise.all([a.getSiteEntries(e,s),a.countSiteEntries(e)]);return{entries:r,totalEntry:n}}case"entry":let{parent:r}=t,{key:n}=r;if("category"===r.type){let[e,t]=await Promise.all([a.getCategoryEntries(n,s),a.countCategoryEntries(n)]);return{entries:e,totalEntry:t}}let[i,l]="all"===n?await Promise.all([a.getAllEntries(s),a.countAllEntries()]):await Promise.all([a.getSiteEntries(n,s),a.countSiteEntries(n)]);return{entries:i,totalEntry:l}}},S=async e=>{if("loading"===c||m.length===p)return;let{entries:t}=await N(s,n,e);g(m.concat(t))},P=(e,t)=>{if(j(e),t){let t=globalThis.document.querySelector("#entry-".concat(e));null==t||t.scrollIntoView({block:"center",inline:"start"})}i&&i(C,A,e)};(0,r.useEffect)(()=>{switch(n.type){case"category":if(y===n.category)return;return f(n.category);case"site":if(y===n.siteKey)return;return f(n.siteKey)}},[n]),(0,r.useEffect)(()=>{v&&(async e=>{let{entries:t,totalEntry:a}=await N(s,n);u("loaded"),g(t),w(a),E(0),e.scrollTo(0,0)})(v)},[y]),(0,r.useEffect)(()=>{if(!(null==b?void 0:b.current))return;let e=new IntersectionObserver(e=>{let[t]=e;"loading"!==c&&t.isIntersecting&&(u("loading"),S(k+1).then(()=>{E(e=>e+1),u("loaded")}))});return e.observe(b.current),()=>{e.disconnect()}},[b,p,m]),(0,r.useEffect)(()=>{let e=e=>{switch(e.code){case"ArrowUp":case"KeyW":{if(!x){P(m[0].key);return}let e=m.findIndex(e=>e.key===x);if(e<=0)return;P(m[e-1].key,!0);return}case"ArrowDown":case"KeyS":{if(!x){P(m[0].key);return}let e=m.findIndex(e=>e.key===x);if(e>=m.length-1)return;P(m[e+1].key,!0);return}}};return globalThis.document.addEventListener("keyup",e),()=>{globalThis.document.removeEventListener("keyup",e)}});let C="entry"===n.type?n.parent.type:n.type,A="entry"===n.type?n.parent.key:"category"===n.type?n.category:n.siteKey;return(0,a.jsxs)("section",{ref:e=>{v=e},className:"pb-4 w-full sm:w-2/3 xl:w-2/6 flex-shrink-0 p-6 overflow-auto overscroll-contain ".concat(t),children:[(0,a.jsx)("a",{className:"cursor-pointer sm:hidden",onClick:o,children:"← Back"}),m.map((e,t)=>(0,a.jsx)(h,{index:t,entry:e,selectedEntryHash:x,selectEntry:P,selectSite:l,entryRef:m.length-5===t&&m.length<p?b:null},e.key)),0===m.length&&(0,a.jsx)("div",{children:(0,a.jsx)("h3",{children:"No contents"})},"none"),(0,a.jsx)("div",{className:"pb-8"})]})},f=e=>{let{className:t,categories:s,totalEntries:n,selectCategory:i,selectSite:l}=e,[o,c]=(0,r.useState)();return(0,a.jsxs)("aside",{className:"w-full sm:w-1/3 xl:w-1/5 flex-shrink-0 p-6 sm:overflow-auto overscroll-contain ".concat(t),children:[(0,a.jsx)("h1",{className:"font-serif",children:"Feeds"}),(0,a.jsxs)("h2",{className:"cursor-pointer",children:[(0,a.jsx)("a",{className:"font-serif no-underline hover:underline mr-2",onClick:()=>l&&l("all"),children:"All sites"}),null!==n&&(0,a.jsxs)("small",{className:"text-sm font-light",children:["(",n,")"]})]}),s.map(e=>(0,a.jsxs)(r.Fragment,{children:[(0,a.jsxs)("h2",{className:"cursor-pointer",children:[(0,a.jsx)("a",{className:"font-serif no-underline hover:underline mr-2",onClick:()=>c(e.title),children:e.title}),(0,a.jsxs)("small",{className:"text-sm font-light",children:["(",e.totalEntries,")"]})]}),e.title===o&&(0,a.jsxs)("ul",{children:[(0,a.jsx)("li",{className:"cursor-pointer",children:(0,a.jsx)("a",{className:"font-serif no-underline hover:underline",onClick:()=>i&&i(o),children:"All sites"})}),e.sites.map(e=>(0,a.jsxs)("li",{className:"cursor-pointer",children:[(0,a.jsx)("a",{className:"font-serif no-underline hover:underline mr-2",onClick:()=>l&&l(e.key),children:e.title}),(0,a.jsxs)("small",{className:"text-sm font-light",children:["(",e.totalEntries,")"]})]},e.key))]})]},e.title)),(0,a.jsx)("div",{className:"pb-8"})]})},m=e=>"article"===e?"block":"hidden xl:block",g=e=>{switch(e){case"article":return"hidden xl:block";case"entries":return"block";default:return"hidden sm:block"}},p=e=>{switch(e){case"article":return"hidden xl:block";case"entries":return"hidden sm:block";default:return"block"}},w=e=>{let t=e.split("/");if(t.shift(),![2,4].includes(t.length))return null;if(2===t.length){if(!t[1].trim())return null;switch(t[0]){case"categories":return{type:"category",category:t[1]};case"sites":return{type:"site",siteKey:t[1]};default:return null}}return t[3].trim()&&["categories","sites"].includes(t[0])&&"entries"===t[2]?{type:"entry",entryKey:t[3],parent:{type:"categories"===t[0]?"category":"site",key:t[1]}}:null},x=async(e,t,s,a)=>{if(!e)return null;let r=d(t);switch(e.type){case"category":case"site":s(null),a("entries");return;case"entry":{let{entryKey:t}=e,n=await r.getContent(t);if(!n)return;s(n),a("article");return}}},j=e=>({type:"UPDATE_PATH",value:e}),k=(e,t)=>{if("UPDATE_PATH"===t.type){let s=t.value;return s===e.pathname?e:(window.history.pushState({},"",s),{...e,pathname:s,location:w(s)})}return e},E=()=>{let[e,t]=(0,r.useState)("loading"),[s,i]=(0,r.useState)("categories"),[l,c]=(0,r.useState)([]),[u,h]=(0,r.useState)(null),[E,b]=(0,r.useState)(null),v=(0,n.useRouter)(),N=(0,n.usePathname)(),[S,P]=(0,r.useReducer)(k,{pathname:N,location:w(N)});return(0,r.useEffect)(()=>{(async()=>{if(!S.location){P(j("/sites/all"));return}if("loading"===e){let e=d("/distro-feeds"),[s,a]=await Promise.all([e.getCategories(),e.countAllEntries()]);b(a),c(s),t("loaded")}await x(S.location,S.pathname,h,i)})();let s=e=>{P(j(N))};return window.addEventListener("popstate",s),()=>{window.removeEventListener("popstate",s)}},[e,S,v]),(0,a.jsx)(a.Fragment,{children:(0,a.jsxs)("div",{className:"prose max-w-none container mx-auto flex flex-row w-screen h-screen",children:["loading"===e&&(0,a.jsx)("div",{className:"p-6",children:(0,a.jsx)("strong",{className:"font-serif text-4xl",children:"Loading database"})}),"loaded"===e&&(0,a.jsxs)(a.Fragment,{children:[(0,a.jsx)(f,{className:p(s),categories:l,totalEntries:E,selectCategory:e=>{P(j("/categories/".concat(e)))},selectSite:e=>{P(j("/sites/".concat(e)))}}),(0,a.jsx)(y,{className:g(s),basePath:S.pathname,locationState:S.location,selectBack:()=>i("categories"),selectSite:e=>{P(j("/sites/".concat(e)))},selectEntry:(e,t,s)=>{P(j("/".concat("category"===e?"categories":"sites","/").concat(t,"/entries/").concat(s)))}}),(0,a.jsx)(o,{className:m(s),content:u,selectBack:()=>{let e=S.location;if("entry"!==e.type)return;let{parent:t}=e,{type:s,key:a}=t;P(j("/".concat("category"===s?"categories":"sites","/").concat(a)))}})]})]})})}}}]);