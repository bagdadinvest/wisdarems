(()=>{"use strict";var o,e={8080:(o,e,t)=>{var a=t(1669),n=t.n(a),r=t(6508);function i(o,e,t){const a=document.createElement("input");a.type="hidden",a.name=e,a.value=t,o.appendChild(a)}function c(){const o=document.querySelectorAll("[data-workflow-action-url]"),e=r.HE.CSRF_TOKEN;o.forEach((o=>{o.addEventListener("click",(t=>{if(t.preventDefault(),"launchModal"in o.dataset)ModalWorkflow({url:o.dataset.workflowActionUrl,onload:{action(o){const e=document.createElement("input");e.type="hidden",e.name="next",e.value=window.location,n()("form",o.body).append(e),o.ajaxifyForm(n()("form",o.body))},success(o,e){window.location.href=e.redirect}}});else{const t=document.createElement("form");t.action=o.dataset.workflowActionUrl,t.method="POST",i(t,"csrfmiddlewaretoken",e),i(t,"next",window.location),document.body.appendChild(t),t.submit()}}),{capture:!0})}))}function l(o){const e=n()(o).get(0);document.querySelectorAll("[data-workflow-action-name]").forEach((o=>{o.addEventListener("click",(t=>{"workflowActionModalUrl"in o.dataset?(t.preventDefault(),t.stopPropagation(),ModalWorkflow({url:o.dataset.workflowActionModalUrl,onload:{action(o){o.ajaxifyForm(n()("form",o.body))},success(t,a){i(e,"action-workflow-action","true"),i(e,"workflow-action-name",o.dataset.workflowActionName),i(e,"workflow-action-extra-data",JSON.stringify(a.cleaned_data)),n()(e).submit()}}})):(i(e,"action-workflow-action","true"),i(e,"workflow-action-name",o.dataset.workflowActionName))}),{capture:!0})}))}window._addHiddenInput=i,window.ActivateWorkflowActionsForDashboard=c,window.ActivateWorkflowActionsForEditView=l;const d=document.currentScript,u=d.dataset.activate,f=d.dataset.confirmCancellationUrl;document.addEventListener("DOMContentLoaded",(()=>{if("dashboard"===u?c():"editor"===u&&l("[data-edit-form]"),f){let o=!1;n()("[name=action-publish]").click((e=>{o||(e.stopImmediatePropagation(),e.preventDefault(),window.ModalWorkflow({url:f,onload:{confirm(t,a){n()("[data-confirm-cancellation]",t.body).click((a=>{o=!0,t.close(),e.currentTarget.click()})),n()("[data-cancel-dialog]",t.body).click((o=>{t.close()}))},no_confirmation_needed(t,a){t.close(),o=!0,e.currentTarget.click()}},triggerElement:e.currentTarget}))}))}}))},1669:o=>{o.exports=jQuery}},t={};function a(o){var n=t[o];if(void 0!==n)return n.exports;var r=t[o]={exports:{}};return e[o](r,r.exports,a),r.exports}a.m=e,o=[],a.O=(e,t,n,r)=>{if(!t){var i=1/0;for(u=0;u<o.length;u++){for(var[t,n,r]=o[u],c=!0,l=0;l<t.length;l++)(!1&r||i>=r)&&Object.keys(a.O).every((o=>a.O[o](t[l])))?t.splice(l--,1):(c=!1,r<i&&(i=r));if(c){o.splice(u--,1);var d=n();void 0!==d&&(e=d)}}return e}r=r||0;for(var u=o.length;u>0&&o[u-1][2]>r;u--)o[u]=o[u-1];o[u]=[t,n,r]},a.n=o=>{var e=o&&o.__esModule?()=>o.default:()=>o;return a.d(e,{a:e}),e},a.d=(o,e)=>{for(var t in e)a.o(e,t)&&!a.o(o,t)&&Object.defineProperty(o,t,{enumerable:!0,get:e[t]})},a.g=function(){if("object"==typeof globalThis)return globalThis;try{return this||new Function("return this")()}catch(o){if("object"==typeof window)return window}}(),a.o=(o,e)=>Object.prototype.hasOwnProperty.call(o,e),a.r=o=>{"undefined"!=typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(o,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(o,"__esModule",{value:!0})},a.j=327,(()=>{var o={327:0};a.O.j=e=>0===o[e];var e=(e,t)=>{var n,r,[i,c,l]=t,d=0;if(i.some((e=>0!==o[e]))){for(n in c)a.o(c,n)&&(a.m[n]=c[n]);if(l)var u=l(a)}for(e&&e(t);d<i.length;d++)r=i[d],a.o(o,r)&&o[r]&&o[r][0](),o[r]=0;return a.O(u)},t=globalThis.webpackChunkwagtail=globalThis.webpackChunkwagtail||[];t.forEach(e.bind(null,0)),t.push=e.bind(null,t.push.bind(t))})();var n=a.O(void 0,[321],(()=>a(8080)));n=a.O(n)})();