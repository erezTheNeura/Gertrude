
# Image Saving Parameters
WorkingDir <- ""
mywidth <- 6
myheight <- 6
myres <- 300


apr_test <- read.csv("April_test_new.csv")
apr_test["month"] <- "04"

mar_test <- read.csv("March_test_new.csv")
mar_test["month"] <- "03"

feb_test <- read.csv("Feb_test_new.csv")
feb_test["month"] <- "02"

jan_test <- read.csv("Jan_test_new.csv")
jan_test["month"] <- "01"

all_test <- rbind(jan_test,feb_test,mar_test,apr_test)

# Plot adoption chart
real_time_users <- c(10,142,139,123,112)
time_line_users <- c(288,216,175,154,133)
png(filename=paste(WorkingDir, "plot_0", ".png", sep=""), units="in", width=mywidth, height=myheight, res=myres)
plot(c("01","02","03","04","05"),round(100*(real_time_users/ time_line_users)),
     ylim = c(0,100),
     type="l",
     main="Ratatouille Adoption Rate",
     xlab="Month", ylab="Adoption Rate",
     xaxt = "n",
     lwd = 3,
     col = "#2E6EA6")
axis(1, at=c(1,2,3,4,5), labels=c("01","02","03","04","05"))
dev.off()

month_col <- c("#082626", "#224573", "#2E6EA6", "#4E9FBF")
  
# Plot accuracy of real time events
png(filename=paste(WorkingDir, "plot_1", ".png", sep=""), units="in", width=mywidth, height=myheight, res=myres)
boxplot(accuracy~month,data=all_test,
        ylim = c(0,100),
        main="Real-Time Events Accuracy",
        xlab="Month", ylab="Accuracy Percentage",
        col = month_col)
dev.off()

png(filename=paste(WorkingDir, "plot_2", ".png", sep=""), units="in", width=mywidth, height=myheight, res=myres)
boxplot(true_positive~month,data=all_test,
        ylim = c(0,100),
        main="True-Positive Events",
        xlab="Month", ylab="True-Positive Percentage",
        col = month_col)
dev.off()

png(filename=paste(WorkingDir, "plot_3", ".png", sep=""), units="in", width=mywidth, height=myheight, res=myres)
boxplot(false_positive~month,data=all_test,
        ylim = c(0,100),
        main="False-Positive Events",
        xlab="Month", ylab="False-Positive Percentage",
        col = month_col)
dev.off()

library(plyr)

# Show activity events
activity_events <- all_test[which(all_test$id == "driving_start" |
                                    all_test$id == "driving_end" |
                                    all_test$id == "walking_start" |
                                    all_test$id == "walking_end" |
                                    all_test$id == "sleeping_start" |
                                    all_test$id == "sleeping_end"
                                    ),]
activity_events$id <- factor(activity_events$id)

activity_events$id<-revalue(activity_events$id,c("driving_start"="Start_driving",
                             "driving_end" = "End_driving",
                             "walking_start" = "Start_walking",
                             "walking_end" = "End_walking",
                             "sleeping_start" = "Fell_asleep",
                             "sleeping_end" = "Woke_up"
                             ))

# Determine activity colors
activity_col <- c("#743966","#743966","#BDBF8A","#BDBF8A","#F2D649","#F2D649")

png(filename=paste(WorkingDir, "plot_4", ".png", sep=""), units="in", width=mywidth, height=myheight, res=myres)
boxplot(accuracy~id,data=activity_events,
        ylim = c(0,100),
        main="Activities' Events",
        xlab="Event id", ylab="Accuracy Percentage",
        col=activity_col,
        xaxt = "n")
id_levels <- c("start","end","start","end","start","end")
axis(1, at=c(1,2,3,4,5,6),labels=id_levels, las=1, cex.axis=0.7,las=1)
legend("topright", inset=.05, title="Activity type",
       c("Driving","Sleeping","Walking"), fill=c("#743966","#BDBF8A","#F2D649"),horiz=TRUE)
dev.off()


# Places events
place_events <- all_test[which(all_test$id == "active_zone_start" |
                                    all_test$id == "active_zone_end" |
                                    all_test$id == "home_start" |
                                    all_test$id == "home_end" |
                                    all_test$id == "work_start" |
                                    all_test$id == "work_end"
),]
place_events$id <- factor(place_events$id)

place_events$id<-revalue(place_events$id,c("active_zone_start"="Arrived_at_active_zone",
                                                 "active_zone_end" = "Left_active_zone",
                                                 "home_start" = "Arrived_home",
                                                 "home_end" = "Left_home",
                                                 "work_start" = "Arrived_at_work",
                                                 "work_end" = "Left_work"))

# Determine place colors
places_col <- c("#BF533B","#BF533B","#8C6C61","#8C6C61","#F2D649","#F2D649")

png(filename=paste(WorkingDir, "plot_5", ".png", sep=""), units="in", width=mywidth, height=myheight, res=myres)
boxplot(accuracy~id,data=place_events,
        ylim = c(0,100),
        main="Places' Events",
        xlab="Event id", ylab="Accuracy Percentage",
        col=places_col,
        #cex.axis = 0.7,
        xaxt = "n"
        )
id_levels <- c("left","arrive","left","arrive","left","arrive")
axis(1, at=c(1,2,3,4,5,6),labels=id_levels, las=1, cex.axis=0.7,las=1)
legend("topright", inset=.05, title="Place type",
       c("Home","Work","Gym"), fill=c("#BF533B","#8C6C61","#F2D649"),horiz=TRUE)
dev.off()

plot(c(),c(),xlim = c(0.9,4.1) ,ylim = c(0,100))
a <- function(event_str,event_color) {
  #event_str = "work_start";
  #event_color = "red"
  lines(c(1,2,3,4),t(all_test[which(all_test$id == event_str),]["accuracy"]),
       type = "l",
       lwd = 3,
       col=event_color
       )  
  #legend("bottomright", "(x,y)", pch = 1, title = event_str)
}


