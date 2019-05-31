//----------------------------------------------------------------------------//
//----------------------------------------------------------------------------//
//----------------------------------------------------------------------------//
<template>
  <div id="roomaircontrol">
    <div class="roomtop">
      <p >{{ room.room_id }} 当前温度 {{ room.current_temper }} </p>
        <button class="returnbtn" v-on:click="check_out"><i class="fa fa-times-rectangle"></i></button>
    </div>
    <div class="roommain">
      <div class="roomcontain roomcontain_2">
          <div class="roomcontainer">
            <p>
              当前费用
              {{ room.fee }}
            </p>
          </div>
          <div class="roomcontainer">
            <p>
              目标温度
              {{ room.target_temper }}
            </p>
          </div>
          <div class="roomcontainer">
            <p>
              当前风速
              {{ room.speed_mode[room.speed] }}
            </p>
          </div>
      </div>
      <div class="roomcontain roomcontain_2">
          <div class="roomcontainer">
              <button class="roomcontainerleft" v-on:click="on">
                <p>开</p>
              </button>
              <button class="roomcontainerright" v-on:click="off">
                <p>关</p>
              </button>
          </div>
          <div class="roomcontainer">
            <button class="roomcontainerleft" v-on:click="temper_add">
              <p>升高温度</p>
            </button>
            <button class="roomcontainerright" v-on:click="temper_min">
              <p>降低温度</p>
            </button>
          </div>
          <div class="roomcontainer">
            <button class="roomcontainerleft" v-on:click="wind_add">
              <p>加大风速</p>
            </button>
            <button class="roomcontainerright" v-on:click="wind_min">
              <p>调小风速</p>
            </button>
          </div>
      </div>
    </div>
  </div>
</template>

<style>
  html, body, #roomaircontrol{
    width: 100%;
    height:100%;
    margin: 0;
    padding: 0;
    background-color: #173446;
    color: #598DAC;
  }
  .roomtop{
    text-align: center;
    width:100%;
    height:79px;
    background-color: #09212F;
    color: #7296AC;
    border-bottom: 1px solid #1A2B36;
  }
  .returnbtn{
    background-color: #09212F;
    position: absolute;
    top: 0;
    right: 0;
    height: 79px;
    width:79px;
    font-size: 28px;
  }
  .returnbtn:hover{
    transition: all 0.7s;
    background-color: #010101;
  }
  .roommain{
    height: calc(100% - 80px);
    width: 100%;
  }
  .roomcontain{
    height: 100%;
    width: calc(50% - 1px);
    display: flex;
    flex-direction:column;
    float: left;
    border-right: 1px solid #598DAC;
  }
  .roomcontain:nth-of-type(2){
    border-right: 0px;
    border-left: 1px solid #598DAC;
  }
  .roomcontainer{
    height: 33.3%;
    width: 100%;
    text-align: center;
  }
  .roomcontainer p,.roomtop p{
    line-height: 2em;
    font-size: 2em;
    position: relative;
    top: calc(50% - 1em);
    margin: 0;
  }
  .roomcontainerleft, .roomcontainerright {
    height: 100%;
    width: 50%;
    float: left;
  }
  button{
    margin: 0;
    padding: 0;
    border: 0;
    outline: none;
    background-color: #173446;
    color: #598DAC;
  }
  button:hover{
    transition: all 0.7s;
    background-color: #1A2B36;
  }
</style>

<script>
// @ is an alias to /src

export default {
  data() {
    return {
      wait: false,
      init_room: true,
      room:{
        room_id: this.$route.query.room_id,//传参
        current_temper: '',               //当前温度
        speed: '',                        //风速
        fee: '',                          //费用
        fee_rate: '',                     //费率
        status: '',                       //空调状态（"服务中", "等待中", "待机"）
        mode: '',                         //模式0制冷，1制热
        service_time: '',                 //工作时间
        target_temper: '',                //目标温度
        highest_temper: '',               //最高温度
        lowest_temper: '',                //最低温度
      },
      speed_mode:['低风速','中风速','高风速'],
    }
  },
  methods: {
    check_out: function(){
      //2.7 退房
      this.$axios({
        method:'get',
        url:'/slave/check_out?room_id='+this.room.room_id,
      }).then(function(response){
        if(response.message == 'OK'){
          this.$router.push("/");
        }
        else alert(response.message);
      }).catch(function(error){
        alert(error);
      })
    },
    on: function(){
      //2.2.1请求开机
      if (this.init_room == true) {//初次请求开机
        this.room.current_temper=26 + Math.floor(Math.random() * 2);
        this.init_room = false;
      }
      this.$axios({
        method:'get',
        url:'/slave/request_on?room_id='+this.room_id+'&current_temper='+this.room.current_temper,
      }).then(function(response){
        if(response.message == 'OK'){
          this.room = response.result;
        }
        else alert(response.message);
      }).catch(function(error){
        alert(error);
      })
    },
    off: function(){
      //2.3请求关机
      this.$axios({
        method:'get',
        url:'/slave/request_off?room_id='+this.room.room_id,
      }).then(function(response){
        if(response.message == 'OK'){
          this.room.speed='';
        }
        else alert(response.message);
      }).catch(function(error){
        alert(error);
      })
    },
    temper_add: function(){
      //2.4 请求改变温度GET /slave/change_temper?room_id=xxx&target_temper=xxx
      if (this.room.target_temper <= (this.room.highest_temper-1)){
        this.$axios({
          method:'get',
          url:'/slave/change_temper?room_id='+this.room.room_id+'&target_temper='+(this.room.target_temper+1),
        }).then(function(response){
          if(response.message == 'OK'){
            this.room.target_temper=this.room.target_temper+1;
          }
          else alert(response.message);
        }).catch(function(error){
          alert(error);
        })
      }
    },
    temper_min: function(){
      //2.4 请求改变温度GET /slave/change_temper?room_id=xxx&target_temper=xxx
      if (this.room.target_temper >= (this.room.lowest_temper+1)){
        this.$axios({
          method:'get',
          url:'/slave/change_temper?room_id='+this.room.room_id+'&target_temper='+(this.room.target_temper-1),
        }).then(function(response){
          if(response.message == 'OK'){
            this.room.target_temper=this.room.target_temper-1;
          }
          else alert(response.message);
        }).catch(function(error){
          alert(error);
        })
      }
    },
    wind_add: function(){
      //2.5 请求改变风速GET /slave/change_speed?room_id=xxx&speed=xxx
      if (this.room.speed <= 1){
        this.$axios({
          method:'get',
          url:'/slave/change_speed?room_id='+this.room.room_id+'&speed='+(this.room.speed+1),
        }).then(function(response){
          if(response.message == 'OK'){
            this.room.speed=this.room.speed+1;
          }
          else alert(response.message);
        }).catch(function(error){
          alert(error);
        })
      }
    },
    wind_min: function(){
      //2.5 请求改变风速GET /slave/change_speed?room_id=xxx&speed=xxx
      if (this.room.speed >= 1){
        this.$axios({
          method:'get',
          url:'/slave/change_speed?room_id='+this.room.room_id+'&speed='+(this.room.speed-1),
        }).then(function(response){
          if(response.message == 'OK'){
            this.room.speed=this.room.speed-1;
          }
          else alert(response.message);
        }).catch(function(error){
          alert(error);
        })
      }
    },
    requesting: function() {
      //2.6 请求费用（及房间状态，用来作为回温依据)
      this.$axios({
        method:'get',
        url:'/slave/request_fee?room_id='+this.room_id,
      }).then(function(response){
        if(response.message == 'OK'){
          this.room = response.result;
        }
        else alert(response.message);
      }).catch(function(error){
        alert(error);
      })
    },
    return_temper:function() {
      //2.6回温+//2.2.2 回温后重新开机
      if (this.status == '等待中'){//回温 当前温度变化 目标温度不变 风速空 费用不变
        this.wait=true;
        this.room.speed='';
        if(this.room.mode==0){//制冷系统，说明要升温
          this.room.current_temper = this.room.current_temper + 0.1;
        }
        else if(this.room.mode==1){//制热系统，说明要降温
          this.room.current_temper = this.room.current_temper - 0.1;
        }
      }
      else if(this.status == '待机'){//回温并不重启  当前温度变化 目标温度空 风速空 费用不变
        this.room.speed='';
        this.room.target_temper='';
        if(this.room.mode==0){//制冷系统，说明要升温
          this.room.current_temper = this.room.current_temper + 0.1;
        }
        else if(this.room.mode==1){//制热系统，说明要降温
          this.room.current_temper = this.room.current_temper - 0.1;
        }
        else if(this.status == '服务中' && this.wait==true){//2.2.2 回温后重新开机
          this.wait=false;
          this.$axios({
            method:'get',
            url:'/slave/request_on?room_id='+this.room_id+'&current_temper='+this.room.current_temper,
            //按照先前设置的目标温度和目标风速创建服务
          }).then(function(response){
            if(response.message == 'OK'){
              this.room = response.result;
            }
            else alert(response.message);
          }).catch(function(error){
            alert(error);
          })
        }
      }
    },
  },
  watch: {
    //2.6 请求费用（及房间状态，用来作为回温依据)
    request_fee: function () {
      // 当开始运行startup的时候,保持3秒轮询
      if (this.init_room == false) {
        var timer1 = setInterval(() => {
          setTimeout(() => {
            this.requesting(); //调用接口的方法
            this.return_temper();
          }, 0)
        }, 12000);//3s
      }
      // 当页面关闭的时候,结束轮询,否则就会一直发请求,
      //使用$once(eventName, eventHandler)一次性监听事件
      this.$once('hook:boforeDestory', () => {
        clearInterval(timer1);
      })
    }
  }
}
</script>
