//----------------------------------------------------------------------------//
//----------------------------------------------------------------------------//
//----------------------------------------------------------------------------//
<template>
  <div id="initpages">
    <div class="initpage"  v-if="!($store.state.set_web)">
      <p>服务器地址</p>
      <input class="serverinput" v-model="$store.state.website">
      <!--<p>房间初始温度</p>
      <input class="serverinput" v-model="$store.state.temper">-->
      <button v-on:click="webset">确定</button>
    </div>
    <div class="initpage" v-show="page_1">
      <button class="initcontain initcontain_2" v-on:click="guest">
        <div class="initcontainer">
          <i class="fa fa-hotel"><p>酒店客人</p></i>
        </div>
      </button>
      <button class="initcontain initcontain_2" v-on:click="host">
        <div class="initcontainer">
          <i class="fa fa-id-badge"><p>工作人员</p></i>
        </div>
      </button>
    </div>

    <div class="initpage" v-show="page_2">
      <button class="initcontain initcontain_5" v-for="room in rooms" :key="room.num" v-on:click="to_room(room.id)">
        <div class="initcontainer">
          <span>{{room.id}}</span>
        </div>
      </button>
    </div>

    <div class="initpage" v-show="page_3">
      <button class="initcontain initcontain_3" v-for="worker in workers" :key="worker.num" v-on:click="to_work(worker.num)">
        <div class="initcontainer">
          <span>{{worker.name}}</span>
        </div>
      </button>
    </div>

  </div>
</template>

<style>
  html, body, #initpages, .initpage{
    width: 100%;
    height:100%;
    margin: 0;
    background-color: #173446;
    color: #598DAC;
  }
  button{
    margin: 0;
    padding: 0;
    border: 0;
    outline: none;
    background-color: #173446;
    color: #598DAC;
  }
  .initcontain{
    display: flex;
    float: left;
  }
  .initcontain_2{
    height: 100%;
    width: 50%;
  }
  .initcontain_3{
    height: 33.3%;
    width: 100%;
  }
  .initcontain_5{
    height: 100%;
    width: 20%;
  }
  .initcontain:hover{
    transition: all 0.7s;
    background-color: #1A2B36;
  }
  .initcontainer{
    margin: auto;
    text-align: center;
  }
  .initcontainer i{
    text-align: center;
    font-size: 10em;
  }
  .initcontainer p{
    margin: 0 auto;
    line-height: 2em;
    font-size: 0.2em;
  }
  .initcontainer span{
    font-size: 2em;
  }
</style>

<script>
// @ is an alias to /src

export default {
  data() {
    return {
      page_1: true,
      page_2: false,
      page_3: false,
      rooms:[
        {num: 1, id:"309c"},
        {num: 2, id:"310c"},
        {num: 3, id:"311c"},
        {num: 4, id:"312c"},
        {num: 5, id:"f3"}
      ],
      workers:[
        {num: 1, name:"前台"},
        {num: 2, name:"经理"},
        {num: 3, name:"管理员"},
      ],
      chose: 0,
    }
  },
  methods: {
    webset: function(){
      this.$store.state.set_web=true;
    },
    guest: function(){
      this.page_1 = false;
      this.page_2 = true;
      this.page_3 = false;
    },
    host: function(){
      this.page_1 = false;
      this.page_2 = false;
      this.page_3 = true;
    },
    to_room: function(id){
      //2.1 入住
      var this_axios = this;
      this_axios.$axios({
        method:'get',
        url:this.$store.state.website+'/slave/check_in?room_id='+id,
      }).then(function(response){
        if(response.data.message == 'OK'){
          this_axios.$router.push({ path: '/room', query: { room_id: id }});
        }
        else alert(response.data.message);
      }).catch(function(error){
        alert(error);
      })

    },
    to_work: function(num){
      if (num==1){
        this.$router.push("reception");
      }
      else if (num==2){
        this.$router.push("manager");
      }
      else if (num==3){
        this.$router.push("server");
      }
    },
  }
}
</script>
