
getwd()
setwd("/Users/paulseitlinger/Documents/GitHub/STIWA")

nLastElements <- 10
fx <- function(d){
	data <- read.csv(d)
	A_rows <- data$A_or_B_track=="A"
	A_data <- data[A_rows,]
	B_data <- data[A_rows==FALSE,]
	unique_tracks_A <- unique(A_data[,"track"])
	unique_tracks_B <- unique(B_data[,"track"])
	
	df_mean <- NULL
	df_revPoints <- NULL
	df_sd <- NULL
	
	for(i in 1:length(unique_tracks_A)){
		i_track <- unique_tracks_A[i]
		A_track_i_rows <- A_data[,"track"]==i_track
		nRows <- length(which(A_track_i_rows)==TRUE)
		A_track_i_CBAs <- A_data[A_track_i_rows,"cur_back_ang"]
		A_track_i_CBAs_tail <- tail(A_track_i_CBAs,nLastElements)
		revPoints <- match(c(1:12),A_data$revs)
		CBA_at_revPoints <- A_track_i_CBAs[revPoints]
		df_mean <- rbind(df_mean,
			data.frame(A_or_B="A",track=i_track,CBA_mean=mean(A_track_i_CBAs_tail),
			CBA_SD=sd(A_track_i_CBAs))
		)
		df_revPoints <- rbind(df_revPoints,
			data.frame(A_or_B="A",track=i_track,revPoints=1:12,CBA=CBA_at_revPoints)
		)
	}
	for(i in 1:length(unique_tracks_B)){
		i_track <- unique_tracks_B[i]
		B_track_i_rows <- B_data[,"track"]==i_track
		nRows <- length(which(B_track_i_rows)==TRUE)
		B_track_i_CBAs <- B_data[B_track_i_rows,"cur_back_ang"]
		B_track_i_CBAs_tail <- tail(B_track_i_CBAs,nLastElements)
		M_B_track <- B_track_i_CBAs
		revPoints <- match(c(1:12),B_data$revs)
		CBA_at_revPoints <- B_track_i_CBAs[revPoints]
		df_mean <- rbind(df_mean,
			data.frame(A_or_B="B",track=i_track,CBA_mean=mean(B_track_i_CBAs_tail),
			CBA_SD=sd(B_track_i_CBAs))
		)
		df_revPoints <- rbind(df_revPoints,
			data.frame(A_or_B="B",track=i_track,revPoints=1:12,CBA=CBA_at_revPoints)
		)
	}
	M_CBA_ATrack <- mean(df_mean[df_mean$A_or_B=="A",]$CBA_mean)
	M_CBA_BTrack <- mean(df_mean[df_mean$A_or_B=="B",]$CBA_mean)
	SD_CBA_ATrack <- mean(df_mean[df_mean$A_or_B=="A",]$CBA_SD)
	SD_CBA_BTrack <- mean(df_mean[df_mean$A_or_B=="B",]$CBA_SD)
	
	df_res_means <- data.frame(M_A=M_CBA_ATrack,SD_A= SD_CBA_ATrack,
	M_B=M_CBA_BTrack,SD_B=SD_CBA_BTrack)
	df_res_CBA_at_revPoints = aggregate(CBA~revPoints*A_or_B,data=df_revPoints,mean)
	df_res_sd <- aggregate(CBA~revPoints*A_or_B,data=df_revPoints,function(i){sd(i,na.rm=T)})
	
	return(list(df_res_means=df_res_means,df_res_sd=df_res_sd,
	df_res_CBA_at_revPoints=df_res_CBA_at_revPoints))
}
fx_out <- fx(d="_5f6hb2#.csv")
fx_out$df_res_means
df_res_CBA_at_revPoints <- fx_out$df_res_CBA_at_revPoints
df_res_SDs <- fx_out$df_res_sd
CBA_at_revPoints_ATrack <- df_res_CBA_at_revPoints[df_res_CBA_at_revPoints$A_or_B=="A","CBA"]
CBA_at_revPoints_BTrack <- df_res_CBA_at_revPoints[df_res_CBA_at_revPoints$A_or_B=="B","CBA"]
SD_at_revPoints_ATrack <- df_res_SDs[df_res_SDs$A_or_B=="A","CBA"]/3
SD_at_revPoints_BTrack <- df_res_SDs[df_res_SDs$A_or_B=="B","CBA"]/3
pdf("CBA_at_revPoints.pdf")
plot(CBA_at_revPoints_ATrack,ylim=c(0,5),type="o",xlab="Number revisions",ylab="Mean resistance (tick angle)")
abline(h=3,lwd=.5)
M_backward <- mean(c(CBA_at_revPoints_ATrack,CBA_at_revPoints_BTrack))
abline(h=M_backward)
arrows(1:12, CBA_at_revPoints_ATrack-SD_at_revPoints_ATrack, 1:12, CBA_at_revPoints_ATrack+SD_at_revPoints_ATrack, length=0.05, angle=90, code=3, lwd = .5) # https://stackoverflow.com/questions/13032777/scatter-plot-with-error-bars
arrows(1:12, CBA_at_revPoints_BTrack-SD_at_revPoints_BTrack, 1:12, CBA_at_revPoints_BTrack+SD_at_revPoints_BTrack, length=0.05, angle=90, code=3, lwd = .5) # https://stackoverflow.com/questions/13032777/scatter-plot-with-error-bars
points(CBA_at_revPoints_BTrack,type="o",lty=2)
legend("bottomright",c("A-Track","B-Track"),lty=c(1,2))
text(4,2,"M (forward) = 3.00")
text(4,2.25,paste("M (backward) =",round(M_backward,2)))
dev.off()

