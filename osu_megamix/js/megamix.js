window.megamixInterpret=(e,state)=>{
let d=Megastream.events.length;
if(d>1000)return{type:"chaos"};
if(state?.combo>50)return{type:"flow"};
return{type:"normal"};
};
