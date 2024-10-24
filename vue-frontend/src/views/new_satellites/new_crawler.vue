<template>
    <div>
        <el-container>
            <!--    SideBar  -->
            <el-aside :width="asideWidth" style="min-height: 100vh; background-color: #001529">
                <div style="
                                    height: 60px;
                                    color: white;
                                    display: flex;
                                    align-items: center;
                                    justify-content: center;
                                ">
                    <img src="@/assets/UCS-Logo.png" alt="" style="width: 120px; height: 60px" />
                </div>

                <el-menu :collapse="isCollapse" :collapse-transition="false" router background-color="#001529"
                    text-color="rgba(255, 255, 255, 0.65)" active-text-color="#fff" style="border: none"
                    :default-active="$route.path">
                    <!-- Master Database Submenu -->
                    <el-submenu index="1">
                        <template slot="title">
                            <i class="el-icon-menu"></i>
                            <span>Master Database</span>
                        </template>
                        <el-menu-item index="/">
                            <i class="el-icon-collection"></i>
                            Master
                        </el-menu-item>
                        <el-menu-item index="/pending">
                            <i class="el-icon-refresh"></i>
                            Pending
                        </el-menu-item>
                        <el-menu-item-group title="History">
                            <el-menu-item index="/edit">
                                <i class="el-icon-edit"></i>
                                Edit
                            </el-menu-item>
                            <el-menu-item index="/manual">
                                <i class="el-icon-document"></i>
                                Manual
                            </el-menu-item>
                        </el-menu-item-group>
                    </el-submenu>
                    <el-submenu index="2">
                        <template slot="title">
                            <i class="el-icon-menu"></i>
                            <span>New Satellites</span>
                        </template>
                        <el-menu-item index="/new_crawler">
                            <i class="el-icon-aim"></i>
                            Crawler
                        </el-menu-item>
                        <el-menu-item index="/new_pending">
                            <i class="el-icon-refresh"></i>
                            Pending
                        </el-menu-item>
                        <el-menu-item-group title="History">
                            <el-menu-item index="/new_edit">
                                <i class="el-icon-edit"></i>
                                Edit
                            </el-menu-item>
                            <el-menu-item index="/new_action">
                                <i class="el-icon-time"></i>
                                Action
                            </el-menu-item>
                        </el-menu-item-group>
                    </el-submenu>
                    <el-submenu index="3">
                        <template slot="title">
                            <i class="el-icon-menu"></i>
                            <span>Duplicate Satellites</span>
                        </template>
                        <el-menu-item index="/duplicate_pending">
                            <i class="el-icon-refresh"></i>
                            Pending
                        </el-menu-item>
                    </el-submenu>
                    <el-menu-item index="/ucs_removed">
                        <i class="el-icon-delete"></i>
                        UCS Removed
                    </el-menu-item>
                    <el-menu-item @click="logout">
                        <i class="el-icon-switch-button"></i>
                        <span slot="title">Logout</span>
                    </el-menu-item>

                </el-menu>
            </el-aside>

            <el-container>
                <!--        Header-->
                <el-header>
                    <!--          <i :class="collapseIcon" style="font-size: 26px" @click="handleCollapse"></i>-->
                    <el-breadcrumb style="margin-left: 20px">
                        <el-breadcrumb-item>Welcome, {{ username }}!</el-breadcrumb-item>
                    </el-breadcrumb>

                    <el-breadcrumb separator-class="el-icon-arrow-right" style="margin-left: 20px">
                        <el-breadcrumb-item>Crawler Page</el-breadcrumb-item>
                    </el-breadcrumb>
                </el-header>


                <!--        Main Page-->
                <el-main>
                    <div class="scraper-page">
                        <el-button type="primary" :disabled="isScraperRunning" @click="runScraper">
                            {{ scraperButtonText }}
                        </el-button>
                    </div>

                    <el-table :data="scrapeRecords" border style="width: 100%">
                        <el-table-column fixed prop="username" label="name"></el-table-column>
                        <el-table-column fixed prop="scrape_date" label="date">
                            <template slot-scope="{row}">
                                {{ new Date(row.scrape_date).toLocaleDateString() }}
                            </template>
                        </el-table-column>
                    </el-table>
                </el-main>

            </el-container>
        </el-container>
    </div>
</template>
  
<script>
import axios from 'axios';
import { Notification } from 'element-ui';

export default {
    data() {
        return {
            isCollapse: false,
            asideWidth: "200px",
            scrapeRecords: [],
            searchQuery: '',
            username: '',
            isScraperRunning: false,
            scraperNotification: null,
        };
    },
    computed: {
        scraperButtonText() {
            return this.isScraperRunning ? 'Running...' : 'Run Crawler';
        }
    },
    mounted() {
        this.getUsername();
        this.fetchScrapeRecords();
    },
    methods: {
        logout() {
            localStorage.removeItem('authToken'); // 清除本地存储中的 token
            this.$router.push('/login'); // 重定向到登录页面
        },
        getUsername() {
            // Retrieve the username from local storage
            this.username = localStorage.getItem('username');
            console.log("Retrieved username:", this.username);
        },
        runScraper() {
            this.isScraperRunning = true;
            this.scraperNotification = Notification({
                title: 'Scraper Status',
                message: 'The scraper is currently running...',
                type: 'info',
                duration: 0 // Keep open indefinitely
            });
            const payload = {
                name: this.username
            };
            axios.post('http://localhost:8000/api/run-scraper', payload)
                .then(response => {
                    console.log('Scraper started:', response.data);
                    setTimeout(() => {
                        this.isScraperRunning = false;
                        this.closeScraperNotification();
                        this.showSuccessNotification();
                    }, 10000); // Adjust the time as needed
                })
                .catch(error => {
                    console.error('Error starting scraper:', error);
                    this.isScraperRunning = false;
                    this.closeScraperNotification();
                });
        },
        fetchScrapeRecords() {
            axios.get('http://localhost:8000/api/scrape-records')
                .then(response => {
                    console.log("Fetched scrape records:", response.data);
                    this.scrapeRecords = response.data;
                })
                .catch(error => {
                    console.error('Error fetching scrape records:', error);
                });
        },
        closeScraperNotification() {
            if (this.scraperNotification) {
                this.scraperNotification.close();
            }
        },
        showSuccessNotification() {
            Notification({
                title: 'Success',
                message: 'Scraper has finished running!',
                type: 'success',
                duration: 5000
            });
        }
    }

}
</script>
  
<style>
.el-table {
    margin-top: 20px;
}

.el-menu--inline {
    background-color: #000c17 !important;
}

.el-menu--inline .el-menu-item {
    background-color: #000c17 !important;
    padding-left: 49px !important;
}

.el-menu-item:hover,
.el-submenu__title:hover {
    color: #fff !important;
}

.el-submenu__title:hover i {
    color: #fff !important;
}

.el-menu-item:hover i {
    color: #fff !important;
}

.el-menu-item.is-active {
    background-color: #1890ff !important;
    border-radius: 5px !important;
    width: calc(100% - 8px);
    margin-left: 4px;
}

.el-menu-item.is-active i,
.el-menu-item.is-active .el-tooltip {
    margin-left: -4px;
}

.el-menu-item {
    height: 40px !important;
    line-height: 40px !important;
}

.el-submenu__title {
    height: 40px !important;
    line-height: 40px !important;
}

.el-submenu .el-menu-item {
    min-width: 0 !important;
}

.el-menu--inline .el-menu-item.is-active {
    padding-left: 45px !important;
}

/*.el-submenu__icon-arrow {*/
/*  margin-top: -5px;*/
/*}*/

.el-aside {
    transition: width 0.3s;
    box-shadow: 2px 0 6px rgba(0, 21, 41, 0.35);
}

.logo-title {
    margin-left: 5px;
    font-size: 20px;
    transition: all 0.3s;
    /* 0.3s */
}

.el-header {
    box-shadow: 2px 0 6px rgba(0, 21, 41, 0.35);
    display: flex;
    align-items: center;
}

/* Style for the button container */
.operation-buttons {
    display: flex;
    flex-direction: column;
    /* Stack buttons vertically */
    align-items: flex-start;
    /* Align buttons to the start of the flex container */
}

/* Style for individual buttons */
.operation-button {
    margin-bottom: 8px;
    /* Add bottom margin to each button except the last one */
}

.operation-button:last-child {
    margin-bottom: 0;
    /* Remove bottom margin from the last button */
}

.el-button+.el-button {
    margin-left: 0px;
}

.el-dropdown {
    margin-left: auto;
}

.el-dropdown-menu {
    padding: 10px;
    /* Add some padding inside the dropdown */
    max-height: 300px;
    /* Set a max height */
    overflow-y: auto;
    /* Add scrollbar if content is too long */
    width: auto;
    /* Adjust width as needed */
}

/* Style for each checkbox in the dropdown */
.el-checkbox {
    display: block;
    /* Make each checkbox take up a full line */
    margin: 5px 0;
    /* Add some margin for spacing */
}

/* Style for the checkbox label */
.el-checkbox__label {
    font-size: 14px;
    /* Adjust font size as needed */
}

.el-table .cell {
    text-overflow: clip;
}

.el-radio-group {
    margin-bottom: 20px;
}

.el-button--small {
    margin: 5px;
}
</style>
  