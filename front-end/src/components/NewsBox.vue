<template>
    <div id="main-frame">
        <div id="frame">
            <div class="best-month-div-items">
                <h3>{{title}}</h3>
                <div class="source-date"><span><a :href="url">{{url}}</a></span>&nbsp;<span>{{publish_date}}</span></div>
                <div class="detail" v-html="summary">{{summary}}</div>
            </div>
            <div><img height="200" width="200" :src="thumbnail"></div>
        </div>
    </div>
</template>

<script>

    export default {

        name: "NewsBox",
        props: ['title', 'url', 'publish_date', 'summary', 'thumbnail','id'],
        data() {
            return {}
        }
    }
</script>

<style scoped>

    #main-frame {
        box-shadow: 0 0 3px lightgray;
        background-color: white;
    }

    #main-frame:hover {
        box-shadow: 0 0 10px lightgray;
    }

    #frame {
        display: flex;
        /*box-shadow: 0 0 3px lightgray;*/
        justify-content: flex-end;
        align-items: flex-start;
        padding: 5px 5px 0 5px;
        min-height: 170px;
        /*width: 313px;*/
        width: 100%;
        flex-basis: 313px;
    }

    #frame > div > img {
        border-color: lightgray;
        border-radius: 5px;
        border-style: solid;
        border-width: 1px;
        margin-top: 15px;
    }

    .best-month-div-items {
        display: flex;
        flex-direction: column;
        /*justify-content: center;*/
        text-align: right;
        align-items: flex-end;
        align-content: space-between;
        padding: 0 5px 0px 5px;
        width: 100%;
        color: black;
    }

    .detail {
        color: gray;
        font-size: .8em;
    }

    .source-date{
        color: darkgray;
        font-size: 0.9em;
    }
</style>
