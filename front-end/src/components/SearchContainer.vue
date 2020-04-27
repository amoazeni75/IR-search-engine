<template>
    <div id="order-div">
        <div class="order-div-items"><p></p></div>
        <div class="order-div-items"><p></p></div>
        <div class="order-div-items"><p></p></div>
        <div class="order-div-items"><h1>سرویس بازیابی اطلاعات</h1></div>
        <div class="order-div-items"><p dir="rtl">پرسمان خود را وارد کنید</p></div>
        <div class="order-div-items" id="search-bar-div">

            <div id="search-bar-left-part">
                <div id="search-input">
                    <input list="suggestion" name="district" placeholder="پرسمان خود را وارد کنید" dir="rtl"
                           v-model="query"
                           @keyup.enter="onSubmit" @click="updateAreaList">
                    <datalist id="suggestion">
                        <!--                        <option>&#128205;جستجو خودکار منطقه شما</option>-->
                        <!--                        <option v-for="(area,index) in areaList" :key="index">{{areaList}}</option>-->
                    </datalist>
                    <div id="question-icon"><i class="fas fa-question"></i></div>
                </div>
                <a>
                    <div class="search-bar-items" @click="onSubmit" id="search-btn-icon-div">

                        <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 18 18">
                            <g fill="none" fill-rule="evenodd">
                                <path d="M0 0h18v18H0z"></path>
                                <g stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                   transform="translate(2 2)">
                                    <circle cx="6.125" cy="6.125" r="6.125"></circle>
                                    <path d="M13.373 13.373l-2.767-2.767"></path>
                                </g>
                                <path d="M0 0h18v18H0z"></path>
                            </g>
                        </svg>
                        <!--<img src="../mocks/search-icon.png">-->
                    </div>
                </a>
            </div>
        </div>
        <div class="order-div-items"><p></p></div>
        <div class="order-div-items"><p></p></div>
        <div class="order-div-items"><p></p></div>

    </div>
</template>

<script>
    import router from '../router'

    export default {
        name: "SearchContainer",
        components: {},
        data() {
            return {
                query: ""
            }
        },
        computed: {
            // areaList: function () {
            //     this.updateAreaList();
            //     let list = [];
            //     for (let i = 0; i < this.restaurantsAddress.length; i++) {
            //         if (!list.includes(this.restaurantsAddress[i].address.area)) {
            //             list.push(this.restaurantsAddress[i].address.area)
            //         }
            //     }
            //     return list;
            // }
        },
        methods: {
            onSubmit() {
                router.push({name: "SearchPage", params: {query: this.query}});
            },
            updateAreaList() {
                // fetch("http://localhost:8000/news/search/".concat(this.query))
                //     .then(response => response.json())
                //     .then((data) => {
                //         this.restaurantsAddress = data;
                //     })
            }
        }
    }
</script>

<style scoped>
    #order-div {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        /*background-color: #bad7ff;*/
        background-color: var(--main-bg-color);
        /*background-color: dodgerblue;*/
        /*background-image: url("../../mocks/pizza.png");*/
        max-height: 513px;
    }

    .order-div-items {
        margin: 10px;
    }

    #search-bar-div {
        display: flex;
        flex-direction: row-reverse;
        padding: 10px;
        width: 50%;
        min-width: 430px;
    }

    #search-bar-left-part {
        display: flex;
        flex-direction: row-reverse;
        width: 100%;
        height: 84px;
        padding: 10px;
        border-radius: 10px 10px 10px 10px;
        background-color: white;
    }

    .white-background {
        background-color: white;
    }

    #search-input {
        display: flex;
        background-color: white;
        border-bottom-right-radius: 10px;
        border-top-right-radius: 10px;
        border: 1px solid lightgray;
        width: 100%;
        max-height: 64px;
    }

    #search-input > input {
        border-width: 0;
        padding: 10px;
        width: 100%;
        font-size: 1.2em;
    }

    #search-input > input:focus {
        outline-width: 0;
    }

    #search-input > div {
        padding: 15px;
    }

    #search-input > div > i {
        background-color: white;
        color: lightgray;
        font-size: 1.8em;
    }

    #search-btn-icon-div {
        padding: 15px 10px 10px 10px;
        border-bottom-left-radius: 10px;
        border-top-left-radius: 10px;
        background: linear-gradient(to right, red, purple);
        /*background: linear-gradient(to right, #bad7ff, dodgerblue);*/
        color: white;
    }

    #search-btn-icon-div > a {
        color: white;
    }
</style>
