<template>
    <div id="SearchPage">
        <MyHeader></MyHeader>
        <div id="loc-search-p" dir="rtl">
            {{newsList.length}}<span> نتایج پرسمان مربوط به </span><span
                class="bold under-line">{{query}}</span><span> پیدا شد.</span>
        </div>
        <div id="search-div">
            <div id="search-input">
                <input name="rest-name" size="40" v-model="newQuery" @keyup.enter="onSubmit"
                       placeholder="پرسمان خود را وارد کنید" dir="rtl">
                <div id="location-icon"><i class="fas fa-search"></i></div>
            </div>
            <div id="dropdown-div">
                <select name="news_sort" id="dropdown-sel" v-model="selected">
                    <option disabled value="">مرتب سازی</option>
                    <option value="date">جدید ترین</option>
                    <option value="similar">مرتبط ترین</option>
                </select>
            </div>
        </div>
        <div id="result-container">
            <div>
                <div class="result-div" id="results-div">
                    <!--                    <router-link v-for="news in showList" :key="news.id"-->
                    <!--                                 :to="{ name: 'NewsPage', params: { id: news.id } }">-->
                    <router-link v-for="news in showList" :key="news.id"
                                 :to="{ name: 'NewsPage', query: { title: news.title, thumbnail: news.thumbnail, content: news.content, myquery: query, id: news.id } }">
                        <NewsBox :title="news.title"
                                 :url="news.url"
                                 :publish_date="news.publish_date"
                                 :summary="news.highlighted"
                                 :thumbnail="news.thumbnail"
                                 :id="news.id">
                        </NewsBox>
                    </router-link>
                </div>
            </div>
        </div>
        <div id="page-number-div">
            <div id="previous-btn" v-on:click="goToPrevious" v-show="pageNumber !== 1">قبلی</div>
            <div>{{pageNumber}}</div>
            <div id="next-btn" v-on:click="goToNext" v-show="pageNumber*pageSize < newsList.length">بعدی</div>
        </div>
        <MyFooter></MyFooter>
    </div>

</template>

<script>
    import MyHeader from "@/components/MyHeader";
    import MyFooter from "@/components/MyFooter";
    import NewsBox from "@/components/NewsBox";


    export default {
        name: "SearchPage",
        components: {NewsBox, MyFooter, MyHeader},
        data() {
            return {
                query: "",
                newQuery: "",
                newsList: [],
                pageNumber: 1,
                pageSize: 10, //number of news per page
                selected: ""
            }
        },
        created() {
            this.query = this.$route.params.query;
            // this.pageNumber = this.$route.params.pageNumber;
        },
        mounted() {
            fetch("http://localhost:8000/news/search/".concat(this.query))
                .then(response => response.json())
                .then((data) => {
                    this.newsList = data;
                });
        },
        computed: {
            sortedList: function () {
                let list = this.newsList;

                function compareDate(a, b) {
                    let aDate = new Date(a.publish_date.replace("th", ""));
                    let bDate = new Date(b.publish_date.replace("th", ""));
                    if (aDate < bDate)
                        return 1;
                    if (aDate > bDate)
                        return -1;
                    return 0;
                }

                function compareSimilar(a, b) {
                    if (a.priority < b.priority)
                        return -1;
                    if (a.priority > b.priority)
                        return 1;
                    return 0;
                }

                if (this.selected == "date") {
                    return list.sort(compareDate);
                } else if (this.selected == "similar") {
                    return list.sort(compareSimilar);
                } else {
                    return this.newsList;
                }
            },

            showList: function () {
                return this.sortedList.slice((this.pageNumber - 1) * this.pageSize, this.pageNumber * this.pageSize)
            },
        },
        methods: {
            onSubmit() {
                fetch("http://localhost:8000/news/search/".concat(this.newQuery))
                    .then(response => response.json())
                    .then((data) => {
                        this.newsList = data;
                    });
                this.query = this.newQuery;
                this.pageNumber = 1;
            },
            goToPrevious() {
                if (this.pageNumber !== 1) {
                    this.pageNumber--;
                }
            },
            goToNext() {
                if (this.pageNumber * this.pageSize < this.newsList.length) {
                    this.pageNumber++;
                }
            }
        }
    }
</script>

<style scoped>

    #loc-search-p {
        text-align: right;
        padding: 10px 50px 10px 10px;
        font-size: 1.2em;
        background-color: white;
    }

    .bold {
        font-weight: bold;
    }

    .under-line {
        border-bottom: 1px solid lightgray;
    }

    #search-div {
        padding: 15px 50px 10px 5px;
        display: flex;
        justify-content: flex-end;
        background-color: white;
    }

    #search-input {
        display: flex;
        border-radius: 5px;
        border: 1px solid lightgray;
        background-color: #fafafa;
        align-content: flex-end;
        justify-content: flex-end;
        align-items: flex-end;
    }

    #search-input > input {
        border-width: 0;
        border-bottom-left-radius: 5px;
        border-bottom-right-radius: 5px;
        padding: 5px;
        background-color: #fafafa;
        font-size: 1em;
    }

    #search-input > input:focus {
        outline-width: 0;
    }

    #search-input > div {
        padding: 5px;
    }

    #search-input > div > i {
        background-color: #fafafa;
        color: gray;
        font-size: 1em;
    }


    #result-container {
        display: flex;
        justify-content: flex-end;
        padding: 50px 20px 10px 10px;
        background-color: #fafafa;
    }

    #results-div {
        width: 100%;
    }

    .result-div {
        display: flex;
        flex-direction: column;
        min-height: 450px;
        /*flex-wrap: wrap;*/
        /*justify-content: flex-end;*/
    }

    .result-div > * {
        margin: 15px 20px 15px 20px;
    }

    #dropdown-div {
        /*padding: 10px 10px 10px 0;*/
        /*border-radius: 0 5px 5px 0;*/
        background-color: white;
    }

    #dropdown-sel {
        /*--dropdown-background-color: gray !important;*/
        border-radius: 5px;
        /*font-family: Shabnam !important;*/
        font-size: 1em;
        padding-left: 5px;
        border-color: lightgray;
        height: 100%;
        /*padding-top: 10px;*/
    }

    #dropdown-sel:focus {
        outline-width: 0;
    }

    #page-number-div {
        display: flex;
        justify-content: center;
    }

    #page-number-div > div {
        margin: 10px;
    }

    #previous-btn:hover, #next-btn:hover {
        cursor: pointer;
        color: dodgerblue;
    }

    #previous-btn, #next-btn {
        font-weight: bold;
    }

</style>
