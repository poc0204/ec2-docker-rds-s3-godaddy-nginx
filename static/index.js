document.addEventListener("DOMContentLoaded",function(){
    let url  ='http://pocworks.store/alldata';
    fetch(url)
    .then(response =>{
        return  response.json()
      })
    .then( data =>{

        data_time = data['data'] - 1
        let show_content = document.getElementById("show_content")
        for(var i = 0 ; i=data_time+1;i++){
            let h2 = document.createElement("h2");
            fetch('http://pocworks.store/show_text/'+data_time)
            .then(response =>{
                return  response.json()
            })
            .then( data =>{
                h2.innerText=data['data'];
            })
            show_content.appendChild(h2);
            let img = document.createElement("img");
            img.src='http://pocworks.store/show_image/'+data_time;
            show_content.appendChild(img);
        
    
           
            let hr = document.createElement("hr");
            show_content.appendChild(hr);
            data_time = data_time-1
        }
    })



})


