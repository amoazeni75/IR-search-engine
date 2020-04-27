<template>
    <div id="NewsPage">
        <MyHeader></MyHeader>
        <h2 class="news-title" dir="rtl">{{title}}</h2>
        <div id="news-container" dir="rtl">
            <div v-show="!content.includes(thumbnail)"><img id="news-img" height="300" width="300" :src="thumbnail">
            </div>
            <div id="news-content" v-html="content">{{content}}</div>
        </div>


        <h2 dir="rtl">خبر های مشابه:</h2>
        <div id="related-news">

            <!--should be uncomment when api created-->

            <router-link class="result-div" v-for="news in similarNewsList" :key="news.id"
                         :to="{ name: 'NewsPage', query: { title: news.title, thumbnail: news.thumbnail, content: news.content, myquery: query, id: news.id } }">
                <NewsBox :title="news.title"
                         :url="news.url"
                         :publish_date="news.publish_date"
                         :summary="news.summary"
                         :thumbnail="news.thumbnail"
                         :id="news.id">
                </NewsBox>
            </router-link>

            <!--should be uncomment when api created-->


            <!--should be removed when api created-->
            <!--            <router-link class="result-div"-->
            <!--                         :to="{ name: 'NewsPage', query: { title: title, thumbnail: thumbnail, content: content, myquery: query, id: id } }">-->
            <!--                <NewsBox :title="title"-->
            <!--                         :url="url"-->
            <!--                         :publish_date="publish_date"-->
            <!--                         :summary="highlighted"-->
            <!--                         :thumbnail="thumbnail"-->
            <!--                         :id="id">-->
            <!--                </NewsBox>-->
            <!--            </router-link>-->

            <!--            <router-link class="result-div"-->
            <!--                         :to="{ name: 'NewsPage', query: { title: title, thumbnail: thumbnail, content: content, myquery: query, id: id } }">-->
            <!--                <NewsBox :title="title"-->
            <!--                         :url="url"-->
            <!--                         :publish_date="publish_date"-->
            <!--                         :summary="highlighted"-->
            <!--                         :thumbnail="thumbnail"-->
            <!--                         :id="id">-->
            <!--                </NewsBox>-->
            <!--            </router-link>-->
            <!--should be removed when api created-->

        </div>
        <MyFooter></MyFooter>
    </div>
</template>

<script>
    import MyHeader from "@/components/MyHeader";
    import MyFooter from "@/components/MyFooter";
    import NewsBox from "@/components/NewsBox";

    export default {
        name: "NewsPage",
        components: {MyFooter, MyHeader, NewsBox},
        data() {
            return {
                id: "",
                title: "",
                content: "",
                query: "",
                thumbnail: "",
                url: "www.url",
                publish_date: "date:1398",
                highlighted: "high text",
                similarNewsList: []
            }
        },
        created() {
            this.id = this.$route.query.id;
            this.title = this.$route.query.title;
            this.content = this.$route.query.content;
            this.thumbnail = this.$route.query.thumbnail;
            this.query = this.$route.query.myquery;
        },
        mounted() {
            fetch("http://localhost:8000/news/search/".concat(this.id))
                .then(response => response.json())
                .then((data) => {
                    this.similarNewsList = data;
                });
        },
        computed: {},
        methods: {
            myFunction() {
            }
        }
    }
</script>

<style scoped>
    .news-title {
        padding: 0 10px 0 10px;
    }

    #news-container {
        padding: 10px;
        min-height: 450px;
    }

    #news-content {
        text-align: right;
    }

    #related-news {
        display: flex;
        flex-direction: column;
        justify-content: flex-end;
        padding: 50px 20px 10px 10px;
        background-color: #fafafa;
    }

    .result-div {
        display: flex;
        flex-direction: column;
        width: 100%;
        margin: 15px 20px 15px 20px;
    }


    #news-img {
        float: right;
        margin: 10px;
    }
</style>
