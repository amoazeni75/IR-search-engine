<template>
    <div id="Home">
        <MyHeader></MyHeader>
        <SearchContainer></SearchContainer>
        <MyFooter></MyFooter>
    </div>
</template>

<script>
    import MyHeader from './components/MyHeader.vue'
    import MyFooter from "@/components/MyFooter";
    import SearchContainer from "@/components/SearchContainer";
    export default {
        name: 'Home',
        components: {
            SearchContainer,
            MyFooter,
            MyHeader
        }
    }
</script>

<style>
</style>
